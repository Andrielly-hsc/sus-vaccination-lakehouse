"""Reference data: IBGE, SINASC (aggregated while reading) and seeds — idempotent reloads."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

from sipni_fake import FakeServer, zip_bytes
from vaccination_lakehouse.config import Settings
from vaccination_lakehouse.ingestion.download import HttpClient
from vaccination_lakehouse.ingestion.reference import (
    data_status,
    denominator_years,
    ingest_reference,
    sinasc_url,
)

pytestmark = pytest.mark.integration

IBGE = [
    {
        "municipio-id": 3205309,
        "municipio-nome": "Vitória",
        "UF-id": 32,
        "UF-sigla": "ES",
        "UF-nome": "Espírito Santo",
        "regiao-id": 3,
        "regiao-sigla": "SE",
        "regiao-nome": "Sudeste",
    },
    {
        "municipio-id": 3550308,
        "municipio-nome": "São Paulo",
        "UF-id": 35,
        "UF-sigla": "SP",
        "UF-nome": "São Paulo",
        "regiao-id": 3,
        "regiao-sigla": "SE",
        "regiao-nome": "Sudeste",
    },
]


def sinasc_zip(year: int, births: dict[str, int], other_year: int = 0) -> bytes:
    """Fictitious SINASC file: one row per birth, with mother-related columns we must not keep."""
    lines = ["contador;CODMUNRES;IDADEMAE;RACACORMAE;DTNASC"]
    counter = 0
    for code, n in births.items():
        for _ in range(n):
            counter += 1
            lines.append(f"{counter};{code};27;1;1503{year}")
    lines += [f"{counter + i + 1};320530;30;2;3112{year - 1}" for i in range(other_year)]
    return zip_bytes(("\r\n".join(lines) + "\r\n").encode("latin-1"), member=f"SINASC_{year}.csv")


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        paths={"data_dir": tmp_path / "data"},
        scope={"ufs": ["ES"], "start_month": "2025-01", "end_month": "2025-03"},
    )


@pytest.fixture
def server(settings: Settings) -> FakeServer:
    srv = FakeServer()
    srv.publish(settings.ingestion.ibge_municipalities_url, json.dumps(IBGE).encode(), '"ibge"')
    base = settings.ingestion.sinasc_base_url
    srv.publish(sinasc_url(base, 2024), sinasc_zip(2024, {"320530": 7, "355030": 3}, 2), '"s24"')
    srv.publish(sinasc_url(base, 2025), sinasc_zip(2025, {"320530": 5}), '"s25"')
    return srv


def load(spark: SparkSession, settings: Settings, name: str):
    return spark.read.format("delta").load(str(settings.paths.table_path(name)))


def test_reference_load_is_idempotent_and_minimised(
    spark: SparkSession, settings: Settings, server: FakeServer
) -> None:
    client = HttpClient(timeout=5, max_retries=0, opener=server, sleep=lambda _: None)

    for _ in range(2):  # second run must give the same tables
        ingest_reference(spark, settings, client)

    ibge = load(spark, settings, "bronze.ref_ibge_municipalities")
    assert ibge.count() == 2
    assert {r["municipio_nome"] for r in ibge.collect()} == {"Vitória", "São Paulo"}

    births = {
        (r["birth_year"], r["residence_municipality_code"]): r["live_births"]
        for r in load(spark, settings, "bronze.ref_sinasc_live_births").collect()
    }
    assert births == {(2024, "320530"): 7, (2024, "355030"): 3, (2025, "320530"): 5}

    landed = sorted((settings.paths.landing_dir / "reference" / "sinasc").glob("sinasc_*.csv"))
    header = landed[0].read_text(encoding="utf-8").splitlines()[0]
    assert header == "birth_year,residence_municipality_code,live_births"  # no mother data (P5)
    assert not list((settings.paths.tmp_dir / "downloads").glob("*.zip"))

    vaccines = load(spark, settings, "bronze.ref_vaccines")
    assert vaccines.count() == 80
    assert load(spark, settings, "bronze.ref_coverage_indicators").count() == 15


def test_sinasc_is_downloaded_again_only_when_republished(
    spark: SparkSession, settings: Settings, server: FakeServer
) -> None:
    client = HttpClient(timeout=5, max_retries=0, opener=server, sleep=lambda _: None)
    ingest_reference(spark, settings, client)
    gets_before = sum(
        1 for method, url, _ in server.requests if method == "GET" and "SINASC" in url
    )

    ingest_reference(spark, settings, client)
    gets_after = sum(1 for method, url, _ in server.requests if method == "GET" and "SINASC" in url)
    assert gets_after == gets_before  # unchanged ETag: no download

    server.publish(
        sinasc_url(settings.ingestion.sinasc_base_url, 2025),
        sinasc_zip(2025, {"320530": 6}),
        '"s25-v2"',
    )
    ingest_reference(spark, settings, client)
    rows = (
        load(spark, settings, "bronze.ref_sinasc_live_births").filter("birth_year = 2025").collect()
    )
    assert [r["live_births"] for r in rows] == [6]


def test_data_status_and_denominator_years(settings: Settings) -> None:
    today = date(2026, 11, 25)
    assert [data_status(y, today) for y in (2024, 2025, 2026)] == [
        "final",
        "preliminary",
        "preview",
    ]
    assert denominator_years(settings) == [2024, 2025]
