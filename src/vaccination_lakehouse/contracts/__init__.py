"""Data contracts (ODCS v3.2.0): loading, Spark schema generation and compatibility checks.

Contracts in ``contracts/`` are the single source of truth for table schemas; code never writes a
``StructType`` by hand for a contracted table (ARCHITECTURE §6.5).
"""

from vaccination_lakehouse.contracts.loader import (
    Contract,
    ContractError,
    Property,
    SchemaObject,
    load_contract,
    load_contracts,
    table,
)

__all__ = [
    "Contract",
    "ContractError",
    "Property",
    "SchemaObject",
    "load_contract",
    "load_contracts",
    "table",
]
