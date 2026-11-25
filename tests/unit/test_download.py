"""Downloader and landing zone: filtering, resume, retries, idempotency, immutability."""

from __future__ import annotations

import gzip
import io
import urllib.error
from pathlib import Path

import pytest

from sipni_fake import COLUMNS, csv_bytes, mixed_month, row, zip_bytes
from vaccination_lakehouse.config import Settings
from vaccination_lakehouse.ingestion.download import (
    HttpClient,
    SourceSchemaError,
    SourceUnavailableError,
    download_month,
    filter_zip,
    months_between,
    sipni_url,
)
from vaccination_lakehouse.ingestion.landing import MANIFEST_NAME, Manifest, atomic_write


class FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, headers: dict[str, str], status: int = 200) -> None:
        super().__init__(body)
        self.headers, self.status = headers, status


class FakeServer:
    """Serves one object per URL with HEAD, GET and Range; can fail on demand."""

    def __init__(self) -> None:
        self.objects: dict[str, tuple[bytes, str]] = {}
        self.fail_next: list[Exception] = []
        self.cut_next_body_at: int | None = None
        self.requests: list[tuple[str, str, str | None]] = []

    def publish(self, url: str, body: bytes, etag: str) -> None:
        self.objects[url] = (body, etag)

    def __call__(self, request, timeout: int) -> FakeResponse:
        url, method = request.full_url, request.get_method()
        byte_range = request.headers.get("Range")
        self.requests.append((method, url, byte_range))
        if self.fail_next:
            raise self.fail_next.pop(0)
        if url not in self.objects:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        body, etag = self.objects[url]
        headers = {"Content-Length": str(len(body)), "ETag": etag, "Last-Modified": "today"}
        if method == "HEAD":
            return FakeResponse(b"", headers)
        status = 200
        if byte_range:
            body, status = body[int(byte_range.split("=")[1].rstrip("-")) :], 206
        if self.cut_next_body_at is not None:
            body, self.cut_next_body_at = body[: self.cut_next_body_at], None
        return FakeResponse(body, headers, status)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        paths={"data_dir": tmp_path / "data"},
        scope={"ufs": ["ES", "SP"], "start_month": "2025-01", "end_month": "2025-01"},
        ingestion={"rows_per_file": 2, "max_retries": 3},
    )


@pytest.fixture
def server() -> FakeServer:
    return FakeServer()


def client_for(server: FakeServer) -> HttpClient:
    return HttpClient(timeout=5, max_retries=3, opener=server, sleep=lambda _: None)


def read_gzip_lines(path: Path) -> list[str]:
    return gzip.decompress(path.read_bytes()).decode("latin-1").splitlines()


def test_months_and_urls() -> None:
    assert months_between("2024-11", "2025-02") == ["2024-11", "2024-12", "2025-01", "2025-02"]
    assert sipni_url("https://x/PNI/csv", "2025-03").endswith("/vacinacao_mar_2025_csv.zip")


def test_filter_keeps_scope_ufs_in_parts_with_header(tmp_path: Path) -> None:
    zip_path = tmp_path / "m.zip"
    zip_path.write_bytes(zip_bytes(csv_bytes(mixed_month(3), extra_lines=["broken;row"])))

    parts, stats = filter_zip(zip_path, tmp_path / "out", "sipni_2025-01_{uf}_e1", ["ES", "SP"], 2)

    assert stats.rows_total == 10 and stats.rows_kept == 6 and stats.rows_unassigned == 1
    assert sorted(parts) == ["ES", "SP"]
    assert [rows for _, rows in parts["ES"]] == [2, 1]  # rotation at rows_per_file
    first = read_gzip_lines(parts["SP"][0][0])
    assert first[0].split(";") == COLUMNS
    assert all(
        line.split(";")[COLUMNS.index("sg_uf_estabelecimento")] == "SP" for line in first[1:]
    )


def test_bytes_are_copied_unchanged_latin1(tmp_path: Path) -> None:
    zip_path = tmp_path / "m.zip"
    zip_path.write_bytes(zip_bytes(csv_bytes([row(1)])))

    parts, _ = filter_zip(zip_path, tmp_path / "out", "x_{uf}", ["ES"], 10)

    assert "UNIDADE DE SAÚDE FICTÍCIA" in read_gzip_lines(parts["ES"][0][0])[1]


def test_header_drift_fails_loudly(tmp_path: Path) -> None:
    changed = csv_bytes([row(1)]).replace(b"co_paciente", b"co_cidadao", 1)
    zip_path = tmp_path / "m.zip"
    zip_path.write_bytes(zip_bytes(changed))

    with pytest.raises(SourceSchemaError, match="co_cidadao"):
        filter_zip(zip_path, tmp_path / "out", "x_{uf}", ["ES"], 10)


def test_download_month_lands_files_and_manifest(settings: Settings, server: FakeServer) -> None:
    url = sipni_url(settings.ingestion.sipni_base_url, "2025-01")
    server.publish(url, zip_bytes(csv_bytes(mixed_month(3))), '"aaaa1111-3"')

    result = download_month(settings, "2025-01", client_for(server))

    landing = settings.paths.landing_dir
    manifest = Manifest(landing / "sipni" / MANIFEST_NAME)
    files = manifest.files("sipni")
    assert result.status == "downloaded" and result.rows_kept == 6 and result.files == 4
    assert sum(f.rows for f in files) == 6
    assert all((landing / f.path).exists() and "aaaa1111" in f.path for f in files)
    assert manifest.completed_source("sipni", "2025-01").extra["rows_total"] == 9
    assert not list((settings.paths.tmp_dir / "downloads").glob("*.zip"))  # zip removed
    assert not list(landing.rglob(".*.tmp"))  # no temporary leftovers


def test_second_run_is_skipped_and_new_etag_adds_files(
    settings: Settings, server: FakeServer
) -> None:
    url = sipni_url(settings.ingestion.sipni_base_url, "2025-01")
    server.publish(url, zip_bytes(csv_bytes(mixed_month(3))), '"aaaa1111-3"')
    client = client_for(server)
    download_month(settings, "2025-01", client)

    assert download_month(settings, "2025-01", client).status == "skipped"

    server.publish(url, zip_bytes(csv_bytes(mixed_month(4))), '"bbbb2222-3"')  # re-published
    result = download_month(settings, "2025-01", client)

    month_dir = settings.paths.landing_dir / "sipni" / "batch" / "2025-01"
    names = sorted(p.name for p in month_dir.iterdir())
    assert result.status == "downloaded"
    assert any("aaaa1111" in n for n in names) and any("bbbb2222" in n for n in names)


def test_widening_the_scope_downloads_again(settings: Settings, server: FakeServer) -> None:
    url = sipni_url(settings.ingestion.sipni_base_url, "2025-01")
    server.publish(url, zip_bytes(csv_bytes(mixed_month(1))), '"aaaa1111"')
    download_month(settings, "2025-01", client_for(server))

    wider = settings.model_copy(
        update={"scope": settings.scope.model_copy(update={"ufs": ["ES", "MG", "SP"]})}
    )

    assert download_month(wider, "2025-01", client_for(server)).status == "downloaded"


def test_interrupted_download_resumes_with_range(tmp_path: Path, server: FakeServer) -> None:
    body = bytes(range(256)) * 100
    server.publish("https://x/f.zip", body, '"e"')
    server.cut_next_body_at = 1000  # first GET ends early (connection dropped)
    client = client_for(server)

    client.download(client.head("https://x/f.zip"), tmp_path / "f.zip")

    assert (tmp_path / "f.zip").read_bytes() == body
    assert ("GET", "https://x/f.zip", "bytes=1000-") in server.requests


def test_transient_errors_are_retried_then_reported(server: FakeServer) -> None:
    server.publish("https://x/f.zip", b"abc", '"e"')
    server.fail_next = [urllib.error.URLError("reset"), TimeoutError("slow")]

    assert client_for(server).head("https://x/f.zip").size == 3

    server.fail_next = [urllib.error.URLError("down")] * 10
    with pytest.raises(SourceUnavailableError):
        client_for(server).head("https://x/f.zip")


def test_not_found_is_not_retried(server: FakeServer) -> None:
    with pytest.raises(SourceUnavailableError, match="404"):
        client_for(server).head("https://x/missing.zip")
    assert len(server.requests) == 1


def test_atomic_write_leaves_nothing_on_failure(tmp_path: Path) -> None:
    target = tmp_path / "file.csv"
    with pytest.raises(RuntimeError), atomic_write(target) as handle:
        handle.write(b"half")
        raise RuntimeError("crash")

    assert not target.exists() and not list(tmp_path.iterdir())
