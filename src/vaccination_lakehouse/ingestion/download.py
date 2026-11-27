"""Download SI-PNI monthly files and keep only the UFs in scope (F03-T01).

Per month:

1. ``HEAD`` the ZIP on S3 → size, ETag, Last-Modified. If the manifest already has this month
   with the same ETag and a scope that covers the requested UFs, skip (idempotent).
2. Download the ZIP to ``data/tmp/downloads`` with **resume** (HTTP ``Range``) and retries with
   exponential backoff.
3. Stream the CSV out of the ZIP **line by line** (never extracted in full: 6–12 GB per month),
   check the header against the source contract, keep the rows whose facility UF is in scope and
   write them as gzip parts of ``rows_per_file`` rows — gzip is not splittable, so several parts
   let Spark read a month in parallel. Bytes are copied unchanged (Latin-1).
4. Record every part and a final ``source`` line in the manifest, then delete the ZIP.
"""

from __future__ import annotations

import gzip
import logging
import random
import time
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import IO

from vaccination_lakehouse import __version__
from vaccination_lakehouse.config import Settings
from vaccination_lakehouse.contracts import load_contract
from vaccination_lakehouse.contracts.loader import CONTRACTS_DIR
from vaccination_lakehouse.ingestion.landing import (
    MANIFEST_NAME,
    Manifest,
    ManifestEntry,
    atomic_write,
    sha256_file,
    short_etag,
    sipni_batch_dir,
    sipni_dir,
)

logger = logging.getLogger(__name__)

PT_MONTHS = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
UF_COLUMN = b"sg_uf_estabelecimento"
RETRYABLE_HTTP = {408, 429, 500, 502, 503, 504}


class SourceUnavailableError(RuntimeError):
    """The source could not be fetched after all retries."""


class SourceSchemaError(RuntimeError):
    """The file does not match the source contract (header changed)."""


def months_between(start: str, end: str) -> list[str]:
    """Inclusive list of ``YYYY-MM`` months."""
    year, month = map(int, start.split("-"))
    end_year, end_month = map(int, end.split("-"))
    months = []
    while (year, month) <= (end_year, end_month):
        months.append(f"{year:04d}-{month:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def sipni_url(base_url: str, month: str) -> str:
    year, number = month.split("-")
    return f"{base_url}/vacinacao_{PT_MONTHS[int(number) - 1]}_{year}_csv.zip"


@dataclass(frozen=True)
class RemoteFile:
    url: str
    size: int
    etag: str
    last_modified: str


class HttpClient:
    """Small HTTP client with timeouts, retries + exponential backoff and resumable downloads.

    Uses only the standard library. ``opener`` and ``sleep`` are injectable for tests.
    """

    def __init__(
        self,
        timeout: int = 120,
        max_retries: int = 5,
        opener: Callable[..., IO[bytes]] = urllib.request.urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.timeout, self.max_retries = timeout, max_retries
        self._open, self._sleep = opener, sleep
        # A generic, honest User-Agent: no personal data (ARCHITECTURE §6.1).
        self.headers = {"User-Agent": f"vaccination-lakehouse/{__version__} (+open-data research)"}

    def _retrying(self, action: Callable[[], object], what: str):
        for attempt in range(self.max_retries + 1):
            try:
                return action()
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRYABLE_HTTP or attempt == self.max_retries:
                    raise SourceUnavailableError(f"{what}: HTTP {exc.code}") from exc
                error: Exception = exc
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                if attempt == self.max_retries:
                    raise SourceUnavailableError(f"{what}: {exc}") from exc
                error = exc
            delay = min(60.0, 2**attempt) * (0.5 + random.random() / 2)  # noqa: S311 (jitter)
            logger.warning("retrying %s in %.1fs (attempt %d): %s", what, delay, attempt + 1, error)
            self._sleep(delay)
        raise AssertionError("unreachable")

    def head(self, url: str) -> RemoteFile:
        def action() -> RemoteFile:
            request = urllib.request.Request(url, method="HEAD", headers=self.headers)
            with self._open(request, timeout=self.timeout) as response:
                return RemoteFile(
                    url=url,
                    size=int(response.headers["Content-Length"]),
                    etag=response.headers.get("ETag", ""),
                    last_modified=response.headers.get("Last-Modified", ""),
                )

        return self._retrying(action, f"HEAD {url}")

    def get_bytes(self, url: str) -> bytes:
        def action() -> bytes:
            request = urllib.request.Request(url, headers=self.headers)
            with self._open(request, timeout=self.timeout) as response:
                return response.read()

        return self._retrying(action, f"GET {url}")

    def download(self, remote: RemoteFile, destination: Path, chunk_size: int = 1 << 20) -> None:
        """Download to ``destination``, resuming a ``.part`` file left by an earlier attempt."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        part = destination.with_name(destination.name + ".part")

        def action() -> None:
            start = part.stat().st_size if part.exists() else 0
            if start < remote.size:
                headers = {**self.headers, "Range": f"bytes={start}-"} if start else self.headers
                request = urllib.request.Request(remote.url, headers=headers)
                with self._open(request, timeout=self.timeout) as response, open(part, "ab") as out:
                    if start and getattr(response, "status", 206) != 206:
                        out.truncate(0)  # server ignored Range: start over
                    for chunk in iter(lambda: response.read(chunk_size), b""):
                        out.write(chunk)
            size = part.stat().st_size
            if size != remote.size:
                raise ConnectionError(f"incomplete download: {size} of {remote.size} bytes")

        if start_size := (part.stat().st_size if part.exists() else 0):
            logger.info("resuming %s at %d bytes", remote.url, start_size)
        self._retrying(action, f"GET {remote.url}")
        part.replace(destination)


class _PartWriter:
    """Gzip parts of at most ``rows_per_file`` rows, each with the header, written atomically."""

    def __init__(self, folder: Path, stem: str, header: bytes, rows_per_file: int) -> None:
        self.folder, self.stem, self.header, self.limit = folder, stem, header, rows_per_file
        self.parts: list[tuple[Path, int]] = []
        self._ctx = None
        self._gzip: gzip.GzipFile | None = None
        self._rows = 0

    def _open(self) -> None:
        path = self.folder / f"{self.stem}_part-{len(self.parts):04d}.csv.gz"
        self._ctx = atomic_write(path)
        handle = self._ctx.__enter__()
        # mtime=0 makes the output byte-identical for identical input (reproducible hashes).
        self._gzip = gzip.GzipFile(fileobj=handle, mode="wb", compresslevel=6, mtime=0)
        self._gzip.write(self.header)
        self.parts.append((path, 0))
        self._rows = 0

    def _close(self) -> None:
        if self._gzip is not None:
            self._gzip.close()
            self._ctx.__exit__(None, None, None)
            path, _ = self.parts[-1]
            self.parts[-1] = (path, self._rows)
            self._gzip = None

    def write(self, line: bytes) -> None:
        if self._gzip is None or self._rows >= self.limit:
            self._close()
            self._open()
        self._gzip.write(line)
        self._rows += 1

    def close(self) -> list[tuple[Path, int]]:
        self._close()
        return self.parts


@dataclass(frozen=True)
class FilterStats:
    rows_total: int
    rows_kept: int
    rows_unassigned: int
    member: str


def expected_header() -> list[str]:
    contract = load_contract(CONTRACTS_DIR / "source" / "sipni_doses.odcs.yaml")
    return contract.get_object("sipni_doses").columns


def filter_zip(
    zip_path: Path,
    out_dir: Path,
    stem_template: str,
    ufs: Iterable[str],
    rows_per_file: int,
    header_columns: list[str] | None = None,
) -> tuple[dict[str, list[tuple[Path, int]]], FilterStats]:
    """Copy the rows of the wanted UFs from the CSV inside ``zip_path`` into gzip parts per UF.

    ``stem_template`` names the parts, e.g. ``"sipni_2025-01_{uf}_ab12cd34"``.
    """
    wanted = {uf.encode() for uf in ufs}
    writers: dict[bytes, _PartWriter] = {}
    total = kept = unassigned = 0
    with zipfile.ZipFile(zip_path) as archive:
        member = max(archive.infolist(), key=lambda info: info.file_size)
        with archive.open(member) as source:
            header = source.readline()
            columns = header.rstrip(b"\r\n").decode("latin-1").split(";")
            expected = header_columns if header_columns is not None else expected_header()
            if columns != expected:
                missing, extra = (
                    sorted(set(expected) - set(columns)),
                    sorted(set(columns) - set(expected)),
                )
                raise SourceSchemaError(
                    f"{member.filename}: header differs from the source contract "
                    f"(missing {missing}, unexpected {extra}, "
                    f"order changed: {not missing and not extra})"
                )
            uf_index = columns.index(UF_COLUMN.decode())
            for line in source:
                total += 1
                fields = line.split(b";", uf_index + 1)
                if len(fields) <= uf_index:
                    unassigned += 1
                    continue
                uf = fields[uf_index]
                if uf in wanted:
                    if uf not in writers:
                        stem = stem_template.format(uf=uf.decode())
                        writers[uf] = _PartWriter(out_dir, stem, header, rows_per_file)
                    writers[uf].write(line)
                    kept += 1
                if total % 2_000_000 == 0:
                    logger.info("%s: %d rows read, %d kept", member.filename, total, kept)
    parts = {uf.decode(): writer.close() for uf, writer in writers.items()}
    return parts, FilterStats(total, kept, unassigned, member.filename)


@dataclass(frozen=True)
class MonthResult:
    month: str
    status: str  # downloaded | skipped
    rows_kept: int = 0
    files: int = 0


def download_month(
    settings: Settings, month: str, client: HttpClient, *, force: bool = False
) -> MonthResult:
    ingestion, paths = settings.ingestion, settings.paths
    ufs = sorted(settings.scope.ufs)
    url = sipni_url(ingestion.sipni_base_url, month)
    manifest = Manifest(sipni_dir(paths.landing_dir) / MANIFEST_NAME)

    remote = client.head(url)
    done = manifest.completed_source("sipni", month)
    if (
        not force
        and done is not None
        and done.source_etag == remote.etag
        and set(ufs) <= set(done.extra.get("ufs", []))
    ):
        logger.info("%s already landed (ETag %s): skipped", month, short_etag(remote.etag))
        return MonthResult(month, "skipped")

    etag8 = short_etag(remote.etag)
    zip_path = paths.tmp_dir / "downloads" / f"vacinacao_{month}_{etag8}.zip"
    logger.info("downloading %s (%.2f GB) → %s", url, remote.size / 1e9, zip_path)
    client.download(remote, zip_path)

    out_dir = sipni_batch_dir(paths.landing_dir) / month
    # The ETag in the name keeps re-published versions of a month side by side (immutability).
    stem_template = f"sipni_{month}_{{uf}}_{etag8}"
    parts, stats = filter_zip(zip_path, out_dir, stem_template, ufs, ingestion.rows_per_file)
    entries = [
        ManifestEntry(
            kind="file",
            dataset="sipni",
            period=month,
            path=path.relative_to(paths.landing_dir).as_posix(),
            rows=rows,
            sha256=sha256_file(path),
            source_url=url,
            source_etag=remote.etag,
            source_last_modified=remote.last_modified,
            extra={"uf": uf},
        )
        for uf, files in parts.items()
        for path, rows in files
    ]
    entries.append(
        ManifestEntry(
            kind="source",
            dataset="sipni",
            period=month,
            rows=stats.rows_kept,
            source_url=url,
            source_etag=remote.etag,
            source_last_modified=remote.last_modified,
            extra={
                "ufs": ufs,
                "rows_total": stats.rows_total,
                "rows_unassigned": stats.rows_unassigned,
                "zip_bytes": remote.size,
                "member": stats.member,
                "files": len(entries),
            },
        )
    )
    manifest.append(*entries)
    if not ingestion.keep_zip:
        zip_path.unlink(missing_ok=True)
    logger.info(
        "%s landed: %d of %d rows kept in %d files (UFs %s)",
        month,
        stats.rows_kept,
        stats.rows_total,
        len(entries) - 1,
        ",".join(ufs),
    )
    return MonthResult(month, "downloaded", stats.rows_kept, len(entries) - 1)


def download(
    settings: Settings,
    months: list[str] | None = None,
    *,
    force: bool = False,
    client: HttpClient | None = None,
) -> list[MonthResult]:
    """Land every month of ``months`` (default: the configured scope)."""
    months = months or months_between(settings.scope.start_month, settings.scope.end_month)
    client = client or HttpClient(
        settings.ingestion.timeout_seconds, settings.ingestion.max_retries
    )
    return [download_month(settings, month, client, force=force) for month in months]
