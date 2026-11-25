"""The single place where SparkSessions are built.

Jobs, tests and notebooks all call :func:`get_spark`, so they share one configuration:
Delta Lake extensions, adaptive query execution, an explicit time zone and laptop-sized
shuffle partitions.
"""

from __future__ import annotations

import logging
from pathlib import Path

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

from vaccination_lakehouse.config import PathsConfig, Settings, SparkConfig, get_settings

logger = logging.getLogger(__name__)


def build_spark_conf(spark_cfg: SparkConfig, paths: PathsConfig) -> dict[str, str]:
    """Return the Spark configuration as a plain dictionary (pure function, easy to test)."""
    metastore = paths.metastore_dir.resolve()
    conf = {
        # Delta Lake: SQL commands (MERGE, OPTIMIZE, VACUUM...) and Delta-aware catalog.
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        # Resources: must be set before the JVM starts (getOrCreate does that in local mode).
        "spark.driver.memory": spark_cfg.driver_memory,
        "spark.sql.shuffle.partitions": str(spark_cfg.shuffle_partitions),
        # Correctness: daily aggregates depend on the session time zone.
        "spark.sql.session.timeZone": spark_cfg.timezone,
        # Performance: AQE coalesces small partitions and splits skewed ones at runtime.
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",
        # Catalog: where managed tables and the local metastore live (both git-ignored).
        "spark.sql.catalogImplementation": spark_cfg.catalog,
        "spark.sql.warehouse.dir": str(metastore / "warehouse"),
        # Keeps Derby's metastore_db/ and derby.log out of the repository root.
        "spark.driver.extraJavaOptions": f"-Dderby.system.home={metastore}",
        "spark.ui.enabled": str(spark_cfg.ui_enabled).lower(),
        "spark.ui.showConsoleProgress": "false",
    }
    conf.update(spark_cfg.extra_conf)
    return conf


def get_spark(settings: Settings | None = None, app_name: str | None = None) -> SparkSession:
    """Create (or return the already running) Delta-enabled SparkSession."""
    settings = settings or get_settings()
    spark_cfg = settings.spark
    Path(settings.paths.metastore_dir).mkdir(parents=True, exist_ok=True)

    builder = SparkSession.builder.appName(app_name or spark_cfg.app_name).master(spark_cfg.master)
    for key, value in build_spark_conf(spark_cfg, settings.paths).items():
        builder = builder.config(key, value)

    # Adds the Delta JAR matching the installed pyspark/delta-spark versions (ADR-0009).
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel(spark_cfg.log_level)
    logger.info(
        "SparkSession ready",
        extra={"spark_version": spark.version, "master": spark_cfg.master},
    )
    return spark
