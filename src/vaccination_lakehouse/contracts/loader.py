"""Load ODCS contracts into typed objects and derive Spark schemas, comments, keys and rules.

Only the subset of ODCS used by this project is modelled (see contracts/README.md); unknown
fields are kept but ignored, so contracts can use more of the standard without breaking the code.

Example::

    from vaccination_lakehouse.contracts import table

    doses = table("silver.vaccination_doses")
    schema = doses.struct_type()            # StructType with comments as column metadata
    keys = doses.primary_key                # ["dose_id"]
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pyspark.sql import types as T

#: Default location of the contracts, relative to the repository root / working directory.
CONTRACTS_DIR = Path("contracts")
LAYERS = ("source", "bronze", "silver", "gold")

#: ODCS ``physicalType`` (Spark SQL type names) → Spark type.
SPARK_TYPES: dict[str, Callable[[], T.DataType]] = {
    "string": T.StringType,
    "int": T.IntegerType,
    "bigint": T.LongType,
    "double": T.DoubleType,
    "boolean": T.BooleanType,
    "date": T.DateType,
    "timestamp": T.TimestampType,
    # Delta/Parquet do not keep element non-nullability, so arrays always allow null elements;
    # declaring containsNull=False would make the written and the read schema differ.
    "array<string>": lambda: T.ArrayType(T.StringType(), containsNull=True),
}


class ContractError(ValueError):
    """A contract file is missing, malformed or does not define what the code asks for."""


class _OdcsModel(BaseModel):
    """Base model: tolerate the ODCS fields we do not model, keep the alias names."""

    model_config = ConfigDict(extra="allow", populate_by_name=True, frozen=True)


class Property(_OdcsModel):
    name: str
    logical_type: str = Field(alias="logicalType")
    physical_type: str | None = Field(default=None, alias="physicalType")
    required: bool = False
    primary_key: bool = Field(default=False, alias="primaryKey")
    primary_key_position: int = Field(default=-1, alias="primaryKeyPosition")
    partitioned: bool = False
    partition_key_position: int = Field(default=-1, alias="partitionKeyPosition")
    classification: str | None = None
    description: str = ""

    @property
    def is_technical(self) -> bool:
        """Ingestion/processing metadata columns start with an underscore."""
        return self.name.startswith("_")

    def spark_type(self) -> T.DataType:
        physical = (self.physical_type or "").lower()
        if physical not in SPARK_TYPES:
            raise ContractError(
                f"column '{self.name}': physicalType '{self.physical_type}' has no Spark mapping"
            )
        return SPARK_TYPES[physical]()


class SchemaObject(_OdcsModel):
    name: str
    physical_name: str = Field(alias="physicalName")
    physical_type: str | None = Field(default=None, alias="physicalType")
    description: str = ""
    properties: tuple[Property, ...] = ()
    quality: tuple[dict[str, Any], ...] = ()

    @property
    def columns(self) -> list[str]:
        return [p.name for p in self.properties]

    @property
    def primary_key(self) -> list[str]:
        keys = [p for p in self.properties if p.primary_key]
        return [p.name for p in sorted(keys, key=lambda p: p.primary_key_position)]

    @property
    def partition_columns(self) -> list[str]:
        parts = [p for p in self.properties if p.partitioned]
        return [p.name for p in sorted(parts, key=lambda p: p.partition_key_position)]

    def column(self, name: str) -> Property:
        for prop in self.properties:
            if prop.name == name:
                return prop
        raise ContractError(f"{self.physical_name} has no column '{name}'")

    def struct_type(
        self, include: Callable[[Property], bool] | None = None, *, with_comments: bool = True
    ) -> T.StructType:
        """Spark schema in contract order; ``nullable = not required``; comments as metadata.

        Args:
            include: optional filter, e.g. ``lambda p: not p.is_technical`` to read a source file.
            with_comments: put each description in the field metadata under ``comment``
                (Delta stores it as the column comment).
        """
        fields = []
        for prop in self.properties:
            if include is not None and not include(prop):
                continue
            metadata = {"comment": prop.description} if with_comments and prop.description else {}
            fields.append(T.StructField(prop.name, prop.spark_type(), not prop.required, metadata))
        return T.StructType(fields)

    def column_comments(self) -> dict[str, str]:
        return {p.name: p.description for p in self.properties if p.description}

    def quality_rules(self) -> list[dict[str, Any]]:
        """Table-level and column-level rules; column rules get a ``column`` key added."""
        rules = [dict(rule) for rule in self.quality]
        for prop in self.properties:
            for rule in getattr(prop, "quality", None) or []:
                rules.append({**rule, "column": prop.name})
        return rules


class Contract(_OdcsModel):
    id: str
    version: str
    status: str | None = None
    name: str | None = None
    api_version: str = Field(alias="apiVersion")
    schema_objects: tuple[SchemaObject, ...] = Field(default=(), alias="schema")
    custom_properties: tuple[dict[str, Any], ...] = Field(default=(), alias="customProperties")
    path: Path | None = None

    @property
    def layer(self) -> str | None:
        for item in self.custom_properties:
            if item.get("property") == "layer":
                return item.get("value")
        return None

    def get_object(self, name: str) -> SchemaObject:
        for obj in self.schema_objects:
            if name in (obj.name, obj.physical_name):
                return obj
        raise ContractError(f"contract {self.id} has no schema object '{name}'")


def load_contract(path: Path | str) -> Contract:
    """Parse one ``*.odcs.yaml`` file."""
    path = Path(path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Contract.model_validate({**raw, "path": path})
    except FileNotFoundError as exc:
        raise ContractError(f"contract not found: {path}") from exc
    except (yaml.YAMLError, ValidationError, TypeError) as exc:
        raise ContractError(f"invalid contract {path}: {exc}") from exc


def load_contracts(contracts_dir: Path | str = CONTRACTS_DIR) -> list[Contract]:
    """All contracts of all layers, sorted by path."""
    root = Path(contracts_dir)
    paths: Iterable[Path] = sorted(
        p for layer in LAYERS for p in (root / layer).glob("*.odcs.yaml")
    )
    return [load_contract(p) for p in paths]


@lru_cache(maxsize=64)
def _index(contracts_dir: str) -> dict[str, SchemaObject]:
    index: dict[str, SchemaObject] = {}
    for contract in load_contracts(contracts_dir):
        for obj in contract.schema_objects:
            if obj.physical_name in index:
                raise ContractError(f"table {obj.physical_name} is defined twice")
            index[obj.physical_name] = obj
    return index


def table(physical_name: str, contracts_dir: Path | str = CONTRACTS_DIR) -> SchemaObject:
    """Schema object of a lakehouse table, e.g. ``table("silver.vaccination_doses")``."""
    index = _index(str(Path(contracts_dir).resolve()))
    if physical_name not in index:
        known = ", ".join(sorted(n for n in index if "." in n))
        raise ContractError(f"no contract defines table '{physical_name}'. Known: {known}")
    return index[physical_name]
