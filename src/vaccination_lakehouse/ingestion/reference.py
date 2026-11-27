"""Reference data into bronze: IBGE municipalities, SINASC live births and seeds (F03-T05).

Every load **replaces its own slice** (``replaceWhere``), so re-running gives the same table:

* IBGE: one slice per download date (``_vintage``) — municipalities are occasionally created.
* SINASC: one slice per birth year. The yearly file has one row per birth with data about the
  mother; it is **aggregated while reading** to counts per residence municipality and the
  microdata is never stored (privacy assessment, rule P5).
* Seeds: the whole table is replaced from ``seeds/*.csv`` and tagged with the git commit.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import subprocess
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from vaccination_lakehouse.config import Settings
from vaccination_lakehouse.contracts import table
from vaccination_lakehouse.ingestion.download import HttpClient
from vaccination_lakehouse.ingestion.landing import (
    MANIFEST_NAME,
    Manifest,
    ManifestEntry,
    atomic_write,
    reference_dir,
    sha256_file,
    short_etag,
)
from vaccination_lakehouse.lakehouse import ensure_table, replace_where
from vaccination_lakehouse.logging_setup import RUN_ID

logger = logging.getLogger(__name__)

SEEDS_DIR = Path("seeds")
IBGE_FIELDS = {  # API field → bronze column (hyphens are not valid column names)
    "municipio-id": "municipio_id",
    "municipio-nome": "municipio_nome",
    "UF-id": "uf_id",
    "UF-sigla": "uf_sigla",
    "UF-nome": "uf_nome",
    "regiao-id": "regiao_id",
    "regiao-sigla": "regiao_sigla",
    "regiao-nome": "regiao_nome",
}


@dataclass(frozen=True)
class ReferenceResult:
    name: str
    status: str
    rows: int


def _now() -> datetime:
    return datetime.now(UTC)


# --------------------------------------------------------------------------------------- IBGE
def ingest_ibge(
    spark: SparkSession, settings: Settings, client: HttpClient, *, force: bool = False
) -> ReferenceResult:
    vintage = date.today().isoformat()
    landing_file = (
        reference_dir(settings.paths.landing_dir, "ibge_municipalities") / f"{vintage}.json"
    )
    url = settings.ingestion.ibge_municipalities_url
    if force or not landing_file.exists():
        payload = client.get_bytes(url)
        json.loads(payload)  # fail before writing if the API returned something else
        with atomic_write(landing_file) as handle:
            handle.write(payload)

    records = json.loads(landing_file.read_text(encoding="utf-8"))
    contract = table("bronze.ref_ibge_municipalities")
    rows = [
        {
            **{column: str(item[field]) for field, column in IBGE_FIELDS.items()},
            "_vintage": date.fromisoformat(vintage),
            "_source_url": url,
            "_batch_id": RUN_ID,
            "_ingested_at": _now(),
        }
        for item in records
    ]
    path = settings.paths.table_path("bronze.ref_ibge_municipalities")
    ensure_table(spark, contract, path, {"layer": "bronze"})
    df = spark.createDataFrame(rows, contract.struct_type(with_comments=False))
    replace_where(df, path, f"_vintage = DATE'{vintage}'")
    logger.info("IBGE municipalities %s: %d rows", vintage, len(rows))
    return ReferenceResult("ibge_municipalities", "loaded", len(rows))


# ------------------------------------------------------------------------------------- SINASC
def sinasc_url(base_url: str, year: int) -> str:
    return f"{base_url}/SINASC_{year}_csv.zip"


def data_status(year: int, today: date | None = None) -> str:
    """Heuristic matching the portal labels on 2026-11-25: final until two years ago, then
    preliminary (previous year) and preview (current year)."""
    current = (today or date.today()).year
    if year <= current - 2:
        return "final"
    return "preliminary" if year == current - 1 else "preview"


def aggregate_sinasc(zip_path: Path, year: int) -> tuple[Counter, int, int]:
    """Count live births per residence municipality for ``year``, streaming the CSV.

    Returns (counts, rows_read, rows_other_year). Only CODMUNRES and DTNASC are read.
    """
    counts: Counter = Counter()
    rows = other_year = 0
    with zipfile.ZipFile(zip_path) as archive:
        member = max(archive.infolist(), key=lambda info: info.file_size)
        with archive.open(member) as raw:
            reader = csv.reader(
                io.TextIOWrapper(raw, encoding="latin-1", newline=""), delimiter=";"
            )
            header = next(reader)
            municipality, birth_date = header.index("CODMUNRES"), header.index("DTNASC")
            for record in reader:
                rows += 1
                if record[birth_date][-4:] != str(year):
                    other_year += 1
                    continue
                counts[record[municipality]] += 1
    return counts, rows, other_year


def ingest_sinasc_year(
    spark: SparkSession, settings: Settings, client: HttpClient, year: int, *, force: bool = False
) -> ReferenceResult:
    url = sinasc_url(settings.ingestion.sinasc_base_url, year)
    folder = reference_dir(settings.paths.landing_dir, "sinasc")
    manifest = Manifest(folder / MANIFEST_NAME)
    remote = client.head(url)
    done = manifest.completed_source("sinasc", str(year))
    landing_file = folder / f"sinasc_{year}_{short_etag(remote.etag)}.csv"

    if force or done is None or done.source_etag != remote.etag:
        zip_path = (
            settings.paths.tmp_dir / "downloads" / f"SINASC_{year}_{short_etag(remote.etag)}.zip"
        )
        client.download(remote, zip_path)
        counts, rows, other_year = aggregate_sinasc(zip_path, year)
        with atomic_write(landing_file, "w") as handle:  # aggregated counts only (P5)
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["birth_year", "residence_municipality_code", "live_births"])
            writer.writerows([year, code, n] for code, n in sorted(counts.items()))
        manifest.append(
            ManifestEntry(
                kind="file",
                dataset="sinasc",
                period=str(year),
                path=landing_file.relative_to(settings.paths.landing_dir).as_posix(),
                rows=len(counts),
                sha256=sha256_file(landing_file),
                source_url=url,
                source_etag=remote.etag,
                source_last_modified=remote.last_modified,
            ),
            ManifestEntry(
                kind="source",
                dataset="sinasc",
                period=str(year),
                rows=sum(counts.values()),
                source_url=url,
                source_etag=remote.etag,
                source_last_modified=remote.last_modified,
                extra={"rows_read": rows, "rows_other_year": other_year, "zip_bytes": remote.size},
            ),
        )
        if not settings.ingestion.keep_zip:
            zip_path.unlink(missing_ok=True)
        status = "downloaded"
    else:
        status = "unchanged"

    contract = table("bronze.ref_sinasc_live_births")
    with open(landing_file, encoding="utf-8", newline="") as handle:
        records = [
            {
                "birth_year": int(r["birth_year"]),
                "residence_municipality_code": r["residence_municipality_code"],
                "live_births": int(r["live_births"]),
                "data_status": data_status(year),
                "_file_hash": sha256_file(landing_file),
                "_batch_id": RUN_ID,
                "_ingested_at": _now(),
            }
            for r in csv.DictReader(handle)
        ]
    path = settings.paths.table_path("bronze.ref_sinasc_live_births")
    ensure_table(spark, contract, path, {"layer": "bronze"})
    df = spark.createDataFrame(records, contract.struct_type(with_comments=False))
    replace_where(df, path, f"birth_year = {year}")
    logger.info("SINASC %d (%s): %d municipalities", year, status, len(records))
    return ReferenceResult(f"sinasc_{year}", status, len(records))


def denominator_years(settings: Settings) -> list[int]:
    """Years whose births are needed: the scope years plus the year before (NT 90/2025 uses
    the previous year while the current one is not consolidated)."""
    first, last = int(settings.scope.start_month[:4]), int(settings.scope.end_month[:4])
    return list(range(first - 1, last + 1))


# -------------------------------------------------------------------------------------- SEEDS
def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def ingest_seeds(
    spark: SparkSession, settings: Settings, seeds_dir: Path = SEEDS_DIR
) -> list[ReferenceResult]:
    commit, results = _git_commit(), []
    for seed in ("coverage_indicators", "vaccines", "doses"):
        name = f"bronze.ref_{seed}"
        contract = table(name)
        with open(seeds_dir / f"{seed}.csv", encoding="utf-8", newline="") as handle:
            rows = [
                {**row, "_git_commit": commit, "_batch_id": RUN_ID, "_ingested_at": _now()}
                for row in csv.DictReader(handle)
            ]
        path = settings.paths.table_path(name)
        ensure_table(spark, contract, path, {"layer": "bronze"})
        df = spark.createDataFrame(rows, contract.struct_type(with_comments=False))
        df.write.format("delta").mode("overwrite").save(str(path))
        results.append(ReferenceResult(seed, "loaded", len(rows)))
    return results


def ingest_reference(
    spark: SparkSession,
    settings: Settings,
    client: HttpClient | None = None,
    *,
    force: bool = False,
) -> list[ReferenceResult]:
    client = client or HttpClient(
        settings.ingestion.timeout_seconds, settings.ingestion.max_retries
    )
    results = [ingest_ibge(spark, settings, client, force=force)]
    results += [
        ingest_sinasc_year(spark, settings, client, year, force=force)
        for year in denominator_years(settings)
    ]
    results += ingest_seeds(spark, settings)
    counts = (
        spark.read.format("delta")
        .load(str(settings.paths.table_path("bronze.ref_sinasc_live_births")))
        .groupBy("birth_year")
        .agg(F.sum("live_births").alias("births"))
    )
    for row in counts.orderBy("birth_year").collect():
        logger.info("SINASC %d: %d live births in the table", row["birth_year"], row["births"])
    return results
