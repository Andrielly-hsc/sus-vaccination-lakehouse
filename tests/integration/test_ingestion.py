"""Landing → bronze on fictitious files: exactly-once, idempotent re-runs, versions, integrity."""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from sipni_fake import COLUMNS, FakeServer, csv_bytes, mixed_month, row, zip_bytes
from vaccination_lakehouse.config import Settings
from vaccination_lakehouse.ingestion.bronze_batch import (
    TABLE,
    ingest_sipni,
    reconcile,
)
from vaccination_lakehouse.ingestion.download import HttpClient, download_month, sipni_url
from vaccination_lakehouse.ingestion.landing import (
    MANIFEST_NAME,
    Manifest,
    ManifestEntry,
    atomic_write,
    sha256_file,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        paths={"data_dir": tmp_path / "data"},
        scope={"ufs": ["ES", "SP"], "start_month": "2025-01", "end_month": "2025-01"},
        ingestion={"rows_per_file": 2, "max_files_per_trigger": 2},
    )


def land(settings: Settings, server: FakeServer, rows, etag: str, month: str = "2025-01") -> None:
    url = sipni_url(settings.ingestion.sipni_base_url, month)
    server.publish(url, zip_bytes(csv_bytes(rows)), etag)
    client = HttpClient(timeout=5, max_retries=0, opener=server, sleep=lambda _: None)
    download_month(settings, month, client)


def bronze(spark: SparkSession, settings: Settings):
    return spark.read.format("delta").load(str(settings.paths.table_path(TABLE)))


def test_ingestion_is_exactly_once_and_idempotent(spark: SparkSession, settings: Settings) -> None:
    server = FakeServer()
    land(settings, server, mixed_month(3), '"aaaa1111"')  # 6 rows in scope, 4 files

    first = ingest_sipni(spark, settings)
    df = bronze(spark, settings)

    assert first.rows == 6 and df.count() == 6
    assert reconcile(spark, settings) == []
    assert df.filter(F.col("_file_hash").isNull() | F.col("_batch_id").isNull()).count() == 0
    assert df.select("_ingest_date").distinct().count() == 1

    second = ingest_sipni(spark, settings)  # nothing new
    assert second.rows == 0 and bronze(spark, settings).count() == 6

    land(settings, server, mixed_month(4), '"bbbb2222"')  # month re-published: 8 rows
    third = ingest_sipni(spark, settings)
    assert third.rows == 8 and bronze(spark, settings).count() == 14
    assert reconcile(spark, settings) == []

    refreshed = ingest_sipni(spark, settings, full_refresh=True)
    assert refreshed.rows == 14 and bronze(spark, settings).count() == 14


def test_values_and_encoding_are_kept_as_text(spark: SparkSession, settings: Settings) -> None:
    land(settings, FakeServer(), [row(1, sg_uf_estabelecimento="ES")], '"cccc3333"')

    ingest_sipni(spark, settings)
    first = bronze(spark, settings).first()

    assert first["no_fantasia_estalecimento"] == "UNIDADE DE SAÚDE FICTÍCIA"  # Latin-1 decoded
    assert first["nu_idade_paciente"] == "0"  # kept as text
    assert first["_corrupt_record"] is None
    assert dict(bronze(spark, settings).dtypes)["dt_vacina"] == "string"


def test_malformed_row_is_kept_in_corrupt_record(spark: SparkSession, settings: Settings) -> None:
    good = csv_bytes([row(1)]).decode("latin-1").splitlines()
    bad = good[1] + ";unexpected-extra-field"
    landing_file = (
        settings.paths.landing_dir
        / "sipni"
        / "batch"
        / "2025-01"
        / "sipni_2025-01_ES_x_part-0000.csv.gz"
    )
    with atomic_write(landing_file) as handle:
        handle.write(gzip.compress(("\r\n".join([*good, bad]) + "\r\n").encode("latin-1")))
    Manifest(settings.paths.landing_dir / "sipni" / MANIFEST_NAME).append(
        ManifestEntry(
            kind="file",
            dataset="sipni",
            period="2025-01",
            path=landing_file.relative_to(settings.paths.landing_dir).as_posix(),
            rows=2,
            sha256=sha256_file(landing_file),
        )
    )

    ingest_sipni(spark, settings)
    df = bronze(spark, settings)

    assert df.count() == 2  # nothing dropped
    corrupt = df.filter(F.col("_corrupt_record").isNotNull()).collect()
    assert len(corrupt) == 1 and "unexpected-extra-field" in corrupt[0]["_corrupt_record"]


def test_changed_landing_file_is_rejected(spark: SparkSession, settings: Settings) -> None:
    land(settings, FakeServer(), [row(1)], '"dddd4444"')
    part = next((settings.paths.landing_dir / "sipni" / "batch" / "2025-01").glob("*.csv.gz"))
    tampered = gzip.decompress(part.read_bytes()).replace(b"VITORIA", b"VILA VELHA")
    part.write_bytes(gzip.compress(tampered))

    with pytest.raises(Exception, match="changed after landing"):
        ingest_sipni(spark, settings)


def test_delta_idempotent_write_skips_a_retried_batch(spark: SparkSession, tmp_path: Path) -> None:
    """What protects bronze when a micro-batch is retried after a crash."""
    path = str(tmp_path / "t")
    batch = spark.range(3)

    for _ in range(2):  # same (txnAppId, txnVersion) twice
        batch.write.format("delta").mode("append").option("txnAppId", "q").option(
            "txnVersion", 7
        ).save(path)

    assert spark.read.format("delta").load(path).count() == 3


def test_bronze_table_has_contract_comments(spark: SparkSession, settings: Settings) -> None:
    land(settings, FakeServer(), [row(1)], '"eeee5555"')
    ingest_sipni(spark, settings)

    fields = {f.name: f for f in bronze(spark, settings).schema}

    assert list(fields)[: len(COLUMNS)] == COLUMNS
    assert "RNDS" in fields["co_documento"].metadata.get("comment", "")


def test_crash_after_delta_commit_does_not_duplicate_on_restart(
    spark: SparkSession, settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The hardest failure: micro-batch 1 is written to Delta, then the process dies before the
    checkpoint records it. On restart Spark replays batch 1; the Delta transaction id
    (txnAppId + txnVersion) makes the replayed write a no-op."""
    from vaccination_lakehouse.ingestion import bronze_batch

    land(settings, FakeServer(), mixed_month(3), '"ffff6666"')  # 4 files → 2 micro-batches of 2

    real_logger = bronze_batch.logger

    class CrashAfterCommit:
        def __getattr__(self, name):
            return getattr(real_logger, name)

        def info(self, message, *args, **kwargs):
            if message.startswith("bronze batch") and args and args[0] == 1:
                raise RuntimeError("simulated crash after the Delta commit of batch 1")
            real_logger.info(message, *args, **kwargs)

    monkeypatch.setattr(bronze_batch, "logger", CrashAfterCommit())
    with pytest.raises(Exception, match="simulated crash"):
        ingest_sipni(spark, settings)
    assert bronze(spark, settings).count() == 6  # batch 1 did reach Delta before the crash

    monkeypatch.setattr(bronze_batch, "logger", real_logger)
    restart = ingest_sipni(spark, settings)  # restart: batch 1 is replayed

    assert restart.rows > 0  # Spark really re-read the files of batch 1...
    history = spark.sql(f"DESCRIBE HISTORY delta.`{settings.paths.table_path(TABLE)}`")
    writes = history.filter("operation = 'WRITE'").count()
    assert writes == 2  # ...but Delta skipped the duplicate commit (batches 0 and 1 only)
    df = bronze(spark, settings)
    assert df.count() == 6  # not 6 + replayed rows
    assert df.select("co_documento").distinct().count() == 6
    assert reconcile(spark, settings) == []
