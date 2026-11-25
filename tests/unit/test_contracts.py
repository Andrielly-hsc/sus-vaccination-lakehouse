"""Contract loader: parsing, Spark schema generation, keys, partitions, comments and rules."""

from __future__ import annotations

from pathlib import Path

import pytest
from pyspark.sql import types as T

from vaccination_lakehouse.contracts import ContractError, load_contract, load_contracts, table
from vaccination_lakehouse.contracts.loader import SPARK_TYPES

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"


def test_all_contracts_load() -> None:
    contracts = load_contracts(CONTRACTS)

    assert len(contracts) >= 15
    assert {c.layer for c in contracts} == {"source", "bronze", "silver", "gold"}


def test_table_lookup_by_physical_name() -> None:
    doses = table("silver.vaccination_doses", CONTRACTS)

    assert doses.name == "vaccination_doses"
    assert doses.primary_key == ["dose_id"]
    assert doses.partition_columns == ["vaccination_month"]


def test_unknown_table_lists_the_known_ones() -> None:
    with pytest.raises(ContractError, match="silver.vaccination_doses"):
        table("silver.does_not_exist", CONTRACTS)


def test_struct_type_follows_contract_order_types_and_nullability() -> None:
    doses = table("silver.vaccination_doses", CONTRACTS)
    schema = doses.struct_type()

    assert schema.fieldNames() == doses.columns
    assert schema["dose_id"].dataType == T.StringType()
    assert schema["dose_id"].nullable is False  # required: true
    assert schema["vaccination_date"].dataType == T.DateType()
    assert schema["age_years"].dataType == T.IntegerType()
    assert schema["is_deleted"].dataType == T.BooleanType()
    assert schema["residence_municipality_code"].nullable is True  # optional
    assert schema["dose_id"].metadata["comment"] == "RNDS document id (business key)."


def test_bronze_read_schema_is_all_strings_without_metadata_columns() -> None:
    raw = table("bronze.sipni_doses_raw", CONTRACTS)
    read_schema = raw.struct_type(include=lambda p: not p.is_technical)

    assert len(read_schema) == 56
    assert {f.dataType for f in read_schema} == {T.StringType()}
    assert read_schema.fieldNames()[0] == "co_documento"


def test_composite_primary_key_is_ordered_by_position() -> None:
    fact = table("gold.fct_doses_daily", CONTRACTS)

    assert fact.primary_key == [
        "vaccination_date",
        "residence_municipality_code",
        "facility_municipality_code",
        "establishment_sk",
        "vaccine_code",
        "dose_code",
        "strategy_code",
    ]


def test_every_lakehouse_column_has_a_spark_type() -> None:
    for contract in load_contracts(CONTRACTS):
        if contract.layer == "source":
            continue  # sources describe files and APIs, not Spark tables
        for obj in contract.schema_objects:
            obj.struct_type()  # raises ContractError on an unmapped physicalType


def test_array_and_bigint_mappings() -> None:
    assert SPARK_TYPES["array<string>"]() == T.ArrayType(T.StringType(), containsNull=True)
    assert SPARK_TYPES["bigint"]() == T.LongType()


def test_quality_rules_include_table_and_column_rules() -> None:
    rules = table("silver.vaccination_doses", CONTRACTS).quality_rules()
    names = {rule.get("name") for rule in rules}

    assert {"unique_dose_id", "registered_after_vaccination", "valid_age"} <= names
    assert all("severity" in rule for rule in rules)


def test_column_comments() -> None:
    comments = table("gold.ind_coverage_yearly", CONTRACTS).column_comments()

    assert "coverage_pct" in comments


def test_unmapped_physical_type_is_reported(tmp_path: Path) -> None:
    contract_file = tmp_path / "x.odcs.yaml"
    contract_file.write_text(
        "apiVersion: v3.2.0\nkind: DataContract\nid: x\nversion: 0.1.0\nschema:\n"
        "  - name: t\n    physicalName: bronze.t\n    properties:\n"
        "      - name: c\n        logicalType: number\n        physicalType: decimal(10,2)\n",
        encoding="utf-8",
    )
    obj = load_contract(contract_file).get_object("t")

    with pytest.raises(ContractError, match="decimal"):
        obj.struct_type()


def test_missing_file_raises_contract_error(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="not found"):
        load_contract(tmp_path / "missing.odcs.yaml")
