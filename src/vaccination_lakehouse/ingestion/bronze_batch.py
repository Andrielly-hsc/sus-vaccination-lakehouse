"""Load SI-PNI landing files into ``bronze.sipni_doses_raw`` (F03-T03, F03-T04).

This is the *Auto Loader* pattern built from open-source parts:

* **Structured Streaming file source** over the landing folder: the **checkpoint** records which
  files were already processed, so every file is read exactly once — no hand-written bookkeeping.
* ``trigger(availableNow=True)``: process everything new, then stop. A "batch" job with streaming
  guarantees; the same code runs continuously with a processing-time trigger.
* ``foreachBatch`` writes each micro-batch with Delta's **idempotent writes** (``txnAppId`` +
  ``txnVersion``): if a micro-batch is retried after a crash, Delta skips the duplicate commit.
* Schema from the contract, never inferred; malformed rows land in ``_corrupt_record`` instead of
  failing the run (``PERMISSIVE``).
"""

from __future__ import annotations

import logging
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from vaccination_lakehouse.config import Settings
from vaccination_lakehouse.contracts import SchemaObject, table
from vaccination_lakehouse.ingestion.landing import (
    MANIFEST_NAME,
    Manifest,
    sha256_file,
    sipni_batch_dir,
    sipni_dir,
)
from vaccination_lakehouse.lakehouse import ensure_table
from vaccination_lakehouse.logging_setup import RUN_ID

logger = logging.getLogger(__name__)

TABLE = "bronze.sipni_doses_raw"
QUERY_NAME = "bronze_sipni_batch"
CORRUPT = "_corrupt_record"


class LandingIntegrityError(RuntimeError):
    """A landing file differs from what the manifest recorded (landing must be immutable)."""


@dataclass(frozen=True)
class IngestResult:
    batches: int
    rows: int


def read_landing(spark: SparkSession, settings: Settings, contract: SchemaObject) -> DataFrame:
    """Streaming DataFrame over the landing files, typed by the contract (all strings)."""
    schema = contract.struct_type(
        include=lambda p: not p.is_technical or p.name == CORRUPT, with_comments=False
    )
    return (
        spark.readStream.format("csv")
        .schema(schema)
        .option("header", True)
        .option("sep", ";")
        .option("encoding", "ISO-8859-1")
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", CORRUPT)
        .option("pathGlobFilter", "*.csv.gz")
        .option("maxFilesPerTrigger", settings.ingestion.max_files_per_trigger)
        .load(str(sipni_batch_dir(settings.paths.landing_dir) / "*"))
        .withColumn("_source_file", F.col("_metadata.file_path"))
    )


def _txn_app_id(checkpoint: Path) -> str:
    """Stable id for Delta idempotent writes, stored next to (and deleted with) the checkpoint."""
    marker = checkpoint.parent / f"{checkpoint.name}.txn_app_id"
    if not marker.exists():
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(f"{QUERY_NAME}-{uuid.uuid4()}", encoding="utf-8")
    return marker.read_text(encoding="utf-8").strip()


def _file_hashes(files: list[str], manifest: Manifest) -> dict[str, str]:
    """SHA-256 of each landing file, checked against the manifest when it has the file."""
    recorded = {Path(e.path).name: e.sha256 for e in manifest.files("sipni")}
    hashes = {}
    for uri in files:
        local = Path(unquote(urlparse(uri).path))  # file:///… URI, percent-encoded
        actual = sha256_file(local)
        expected = recorded.get(local.name)
        if expected and expected != actual:
            raise LandingIntegrityError(f"{local.name} changed after landing (hash mismatch)")
        hashes[uri] = actual
    return hashes


def ingest_sipni(
    spark: SparkSession,
    settings: Settings,
    *,
    available_now: bool = True,
    full_refresh: bool = False,
) -> IngestResult:
    """Load new landing files into bronze; returns the number of micro-batches and rows."""
    contract = table(TABLE)
    path = settings.paths.table_path(TABLE)
    checkpoint = settings.paths.checkpoint_path(QUERY_NAME)
    if full_refresh:
        logger.warning("full refresh: deleting %s and its checkpoint", TABLE)
        shutil.rmtree(path, ignore_errors=True)
        shutil.rmtree(checkpoint, ignore_errors=True)
        checkpoint.parent.joinpath(f"{checkpoint.name}.txn_app_id").unlink(missing_ok=True)

    ensure_table(
        spark, contract, path, {"layer": "bronze", "contract_id": "vaxlake-bronze-sipni-doses-raw"}
    )
    manifest = Manifest(sipni_dir(settings.paths.landing_dir) / MANIFEST_NAME)
    app_id = _txn_app_id(checkpoint)
    columns = contract.columns

    def write_batch(batch: DataFrame, batch_id: int) -> None:
        batch = batch.persist()  # used twice: list the files, then write the rows
        try:
            files = [r[0] for r in batch.select("_source_file").distinct().collect()]
            if files:
                _write(batch, batch_id, files)
        finally:
            batch.unpersist()

    def _write(batch: DataFrame, batch_id: int, files: list[str]) -> None:
        hashes = _file_hashes(files, manifest)
        mapping = F.create_map(*[F.lit(x) for pair in hashes.items() for x in pair])
        out = batch.withColumns(
            {
                "_file_hash": mapping[F.col("_source_file")],
                "_batch_id": F.lit(f"{RUN_ID}-{batch_id}"),
                "_ingested_at": F.current_timestamp(),
                "_ingest_date": F.current_date(),
            }
        ).select(*columns)
        (
            out.write.format("delta")
            .mode("append")
            .option("txnAppId", app_id)
            .option("txnVersion", batch_id)
            .save(str(path))
        )
        logger.info("bronze batch %d: %d files", batch_id, len(files))

    writer = (
        read_landing(spark, settings, contract)
        .writeStream.queryName(QUERY_NAME)
        .option("checkpointLocation", str(checkpoint))
        .foreachBatch(write_batch)
    )
    writer = (
        writer.trigger(availableNow=True)
        if available_now
        else writer.trigger(processingTime="10 seconds")
    )
    query = writer.start()
    query.awaitTermination()
    progress = query.recentProgress
    rows = sum(p.get("numInputRows", 0) for p in progress)
    batches = sum(1 for p in progress if p.get("numInputRows", 0) > 0)
    logger.info("bronze ingestion finished: %d rows in %d batches", rows, batches)
    return IngestResult(batches, rows)


def reconcile(spark: SparkSession, settings: Settings) -> list[str]:
    """Compare bronze row counts per file with the landing manifest; return mismatches."""
    path = str(settings.paths.table_path(TABLE))
    counts = {
        Path(r["_source_file"]).name: r["n"]
        for r in spark.read.format("delta")
        .load(path)
        .groupBy("_source_file")
        .agg(F.count("*").alias("n"))
        .collect()
    }
    manifest = Manifest(sipni_dir(settings.paths.landing_dir) / MANIFEST_NAME)
    problems = []
    for entry in manifest.files("sipni"):
        name = Path(entry.path).name
        if name not in counts:
            problems.append(f"{name}: in the manifest but not in bronze")
        elif counts[name] != entry.rows:
            problems.append(f"{name}: manifest {entry.rows} rows, bronze {counts[name]}")
    return problems
