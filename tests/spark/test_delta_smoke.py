"""Smoke tests: the SparkSession works and Delta Lake is wired in correctly."""

from __future__ import annotations

from pyspark.sql import Row, SparkSession
from pyspark.testing import assertDataFrameEqual


def test_session_uses_project_settings(spark: SparkSession) -> None:
    assert spark.conf.get("spark.sql.session.timeZone") == "America/Sao_Paulo"
    assert spark.conf.get("spark.sql.shuffle.partitions") == "2"


def test_delta_round_trip(spark: SparkSession, tmp_path) -> None:
    path = str(tmp_path / "doses")
    expected = spark.createDataFrame(
        [Row(dose_id="a", doses=1), Row(dose_id="b", doses=2)],
    )

    expected.write.format("delta").save(path)
    actual = spark.read.format("delta").load(path)

    assertDataFrameEqual(actual, expected)  # order-insensitive by default


def test_merge_is_idempotent(spark: SparkSession, tmp_path) -> None:
    """The core promise of the silver layer, in miniature: re-applying a batch changes nothing."""
    from delta.tables import DeltaTable

    path = str(tmp_path / "silver")
    spark.createDataFrame([Row(dose_id="a", doses=1)]).write.format("delta").save(path)
    batch = spark.createDataFrame([Row(dose_id="a", doses=1), Row(dose_id="b", doses=2)])

    for _ in range(2):  # same batch twice, e.g. a retry after a crash
        (
            DeltaTable.forPath(spark, path)
            .alias("t")
            .merge(batch.alias("s"), "t.dose_id = s.dose_id")
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )

    result = spark.read.format("delta").load(path)
    assertDataFrameEqual(result, batch)
