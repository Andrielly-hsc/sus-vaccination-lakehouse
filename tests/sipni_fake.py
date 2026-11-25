"""Fictitious SI-PNI rows in the real file format (Latin-1, ';', CRLF, 56 columns).

No real person is represented: identifiers are synthetic and values are drawn from small fixed
lists. Used by the downloader, landing and bronze tests.
"""

from __future__ import annotations

import io
import urllib.error
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COLUMNS: list[str] = [
    p["name"]
    for p in yaml.safe_load(
        (ROOT / "contracts" / "source" / "sipni_doses.odcs.yaml").read_text(encoding="utf-8")
    )["schema"][0]["properties"]
]

_DEFAULTS = {
    "tp_sexo_paciente": "F",
    "co_raca_cor_paciente": "99",
    "no_raca_cor_paciente": "SEM INFORMACAO",
    "co_municipio_paciente": "320530",
    "co_pais_paciente": "10",
    "no_municipio_paciente": "VITORIA",
    "no_pais_paciente": "BRASIL",
    "sg_uf_paciente": "ES",
    "ds_nacionalidade_paciente": "B",
    "co_cnes_estabelecimento": "1234567",
    "no_razao_social_estabelecimento": "SECRETARIA MUNICIPAL DE SAUDE",
    "no_fantasia_estalecimento": "UNIDADE DE SAÚDE FICTÍCIA",
    "co_municipio_estabelecimento": "320530",
    "no_municipio_estabelecimento": "VITORIA",
    "sg_uf_estabelecimento": "ES",
    "co_vacina": "42",
    "sg_imunobiologico": "Penta",
    "dt_vacina": "2025-01-15",
    "co_dose_vacina": "1",
    "ds_tipo_dose": "1ª Dose",
    "dt_entrada_rnds": "2025-02-10",
    "co_sistema_origem": "18602",
    "ds_sistema_origem": "ESUS APS - NACIONAL (OFFLINE)",
    "st_documento": "final",
    "co_estrategia_vacinacao": "1",
    "no_estrategia": "Rotina",
    "ds_nome": "vacina adsorvida difteria, tétano, pertussis, hepatite B e Hib",
    "nu_idade_paciente": "0",
    "no_uf_paciente": "ESPIRITO SANTO",
    "no_uf_estabelecimento": "ESPIRITO SANTO",
}


def row(index: int, **overrides: str) -> dict[str, str]:
    values = {column: "" for column in COLUMNS}
    values.update(_DEFAULTS)
    values["co_documento"] = f"00000000-0000-4000-8000-{index:012d}"
    values["co_paciente"] = f"fake{index:028x}"
    values.update(overrides)
    return values


def csv_bytes(rows: list[dict[str, str]], extra_lines: list[str] = ()) -> bytes:
    lines = [";".join(COLUMNS)]
    lines += [";".join(r[c] for c in COLUMNS) for r in rows]
    lines += list(extra_lines)
    return ("\r\n".join(lines) + "\r\n").encode("latin-1")


def zip_bytes(csv: bytes, member: str = "vacinacao_jan_2025.csv") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, csv)
    return buffer.getvalue()


def mixed_month(n_per_uf: int = 3, month: str = "2025-01") -> list[dict[str, str]]:
    """Rows from ES, SP and MG (MG is out of the test scope)."""
    rows, index = [], 0
    for uf in ("ES", "SP", "MG"):
        for _ in range(n_per_uf):
            index += 1
            rows.append(row(index, sg_uf_estabelecimento=uf, dt_vacina=f"{month}-15"))
    return rows


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
