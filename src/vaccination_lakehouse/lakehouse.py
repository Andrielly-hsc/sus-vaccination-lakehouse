"""Helpers to create and write lakehouse tables from their contracts."""

from __future__ import annotations

from pathlib import Path

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession

from vaccination_lakehouse.contracts import SchemaObject


def ensure_table(
    spark: SparkSession,
    contract: SchemaObject,
    path: Path,
    properties: dict[str, str] | None = None,
) -> None:
    """Create the Delta table with the contract's columns, comments and partitioning (no-op if
    it exists). Column comments and table properties make the table self-describing."""
    builder = DeltaTable.createIfNotExists(spark).location(str(path))
    for prop in contract.properties:
        builder = builder.addColumn(
            prop.name, prop.spark_type(), nullable=not prop.required, comment=prop.description
        )
    if contract.partition_columns:
        builder = builder.partitionedBy(*contract.partition_columns)
    if contract.description:
        builder = builder.comment(contract.description)
    for key, value in (properties or {}).items():
        builder = builder.property(key, value)
    builder.execute()


def replace_where(df: DataFrame, path: Path, predicate: str) -> None:
    """Atomically replace the rows matching ``predicate`` (idempotent reload of a slice)."""
    df.write.format("delta").mode("overwrite").option("replaceWhere", predicate).save(str(path))
