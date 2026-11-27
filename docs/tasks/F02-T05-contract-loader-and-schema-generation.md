# F02-T05 — Generate Spark schemas from contracts

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | Done |
| **Estimate** | 3 h |
| **Depends on** | [F02-T04](F02-T04-data-contracts-odcs.md) |
| **Branch** | `feat/F02-T05-contract-loader-and-schema-generation` |

## Description

Code that reads contracts and produces Spark `StructType`s, column comments and rule lists; plus a breaking-change check.

## Steps

1. `contracts/loader.py`: parse YAML into typed Python objects (pydantic)
2. `to_struct_type(contract)`; `column_comments(contract)`; `quality_rules(contract)`
3. `scripts/check_contract_compat.py`: compare a contract with `main`; removed/renamed/retyped column without major bump → fail
4. Unit tests for type mapping and compatibility rules; wire the check into CI

## Acceptance criteria

- [ ] Bronze/silver jobs obtain their schemas only through the loader — API ready (`table(...).struct_type()`); enforced as jobs are written in F03/F05
- [x] CI fails on an unversioned breaking change (tested with a fixture)

## Deliverables

- `src/vaccination_lakehouse/contracts/loader.py`
- `scripts/check_contract_compat.py`
- `src/vaccination_lakehouse/contracts/compat.py`
- `tests/unit/test_contracts.py`, `tests/unit/test_contract_compat.py`, `tests/spark/test_contract_schemas.py`
- CI step *Check data-contract versions against the base branch*

## Why this matters (best practice)

'Single source of truth' only works if the other artefacts are generated, not copied. Automated compatibility checks are how teams evolve schemas without breaking downstream consumers.

## Notes

- API: `table("silver.vaccination_doses").struct_type()` returns the Spark schema in contract order, `nullable = not required`, with each description as the column comment; `primary_key`, `partition_columns`, `column_comments()` and `quality_rules()` come from the same object. `struct_type(include=lambda p: not p.is_technical)` gives the read schema of a source file (56 string columns).
- pydantic models cover only the ODCS subset we use (`extra="allow"`), so contracts can use more of the standard without breaking the code.
- **Real finding:** Delta/Parquet does not keep `containsNull=False` for array elements; the first Spark run failed for the two array columns. The mapping now uses `containsNull=True`, which is what Delta stores. The Spark test writes and re-reads an empty Delta table for all 21 lakehouse schemas and checks names, types and comments.
- Compatibility rules (`compat.py`): removing/renaming/retyping a column, making it required, changing keys, partitioning or allowed values, or adding an error-level rule is **breaking** (major; minor before 1.0.0, as SemVer allows); adding optional columns or warning rules is additive (minor); text edits need no bump. Removing a contract file is an error (use `status: retired`).
- End-to-end check of the script: dropping a column without a bump failed with exit code 1 and a clear message; the same change with a minor bump (0.x) passed.
- Ruff rule N812 disabled: `from pyspark.sql import functions as F, types as T` is the PySpark convention.
- Results: 59 unit tests on Windows, **83 tests (incl. Spark) in WSL2**, coverage 91 %.
