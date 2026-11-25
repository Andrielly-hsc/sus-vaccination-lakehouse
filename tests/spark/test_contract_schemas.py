"""Every lakehouse contract produces a schema that Spark and Delta accept, comments included."""

from __future__ import annotations

from pathlib import Path

import pytest
from pyspark.sql import SparkSession

from vaccination_lakehouse.contracts import load_contracts

ROOT = Path(__file__).resolve().parents[2]
LAKEHOUSE_OBJECTS = [
    obj
    for contract in load_contracts(ROOT / "contracts")
    if contract.layer != "source"
    for obj in contract.schema_objects
]


@pytest.mark.parametrize("obj", LAKEHOUSE_OBJECTS, ids=lambda o: o.physical_name)
def test_contract_schema_round_trips_through_delta(spark: SparkSession, tmp_path, obj) -> None:
    schema = obj.struct_type()
    path = str(tmp_path / obj.name)

    spark.createDataFrame([], schema).write.format("delta").save(path)
    stored = spark.read.format("delta").load(path).schema

    assert [(f.name, f.dataType) for f in stored] == [(f.name, f.dataType) for f in schema]
    first = next(f for f in stored if obj.column(f.name).description)
    assert first.metadata.get("comment") == obj.column(first.name).description
