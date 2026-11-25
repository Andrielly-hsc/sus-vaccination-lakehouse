# F02-T05 — Generate Spark schemas from contracts

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | To Do |
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

- [ ] Bronze/silver jobs obtain their schemas only through the loader
- [ ] CI fails on an unversioned breaking change (tested with a fixture)

## Deliverables

- `src/vaccination_lakehouse/contracts/loader.py`
- `scripts/check_contract_compat.py`
- `tests/unit/test_contracts.py`

## Why this matters (best practice)

'Single source of truth' only works if the other artefacts are generated, not copied. Automated compatibility checks are how teams evolve schemas without breaking downstream consumers.

## Notes

_Add decisions, problems found and links to the PR here while working._
