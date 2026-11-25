"""The Spark configuration is a pure function, so it is tested without starting a JVM."""

from __future__ import annotations

from vaccination_lakehouse.config import PathsConfig, SparkConfig
from vaccination_lakehouse.spark import build_spark_conf


def test_delta_extensions_and_catalog_are_configured() -> None:
    conf = build_spark_conf(SparkConfig(), PathsConfig())

    assert conf["spark.sql.extensions"] == "io.delta.sql.DeltaSparkSessionExtension"
    assert conf["spark.sql.catalog.spark_catalog"].endswith("DeltaCatalog")


def test_values_come_from_config() -> None:
    cfg = SparkConfig(driver_memory="1g", shuffle_partitions=4, ui_enabled=False)

    conf = build_spark_conf(cfg, PathsConfig())

    assert conf["spark.driver.memory"] == "1g"
    assert conf["spark.sql.shuffle.partitions"] == "4"
    assert conf["spark.ui.enabled"] == "false"
    assert conf["spark.sql.session.timeZone"] == "America/Sao_Paulo"
    assert conf["spark.sql.adaptive.enabled"] == "true"


def test_metastore_lives_under_data_dir(tmp_path) -> None:
    conf = build_spark_conf(SparkConfig(), PathsConfig(data_dir=tmp_path))

    metastore = str((tmp_path / "metastore").resolve())
    assert conf["spark.sql.warehouse.dir"].startswith(metastore)
    assert metastore in conf["spark.driver.extraJavaOptions"]


def test_extra_conf_overrides_defaults() -> None:
    cfg = SparkConfig(extra_conf={"spark.sql.adaptive.enabled": "false", "spark.foo": "bar"})

    conf = build_spark_conf(cfg, PathsConfig())

    assert conf["spark.sql.adaptive.enabled"] == "false"
    assert conf["spark.foo"] == "bar"
