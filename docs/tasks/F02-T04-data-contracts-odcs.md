# F02-T04 — Write ODCS contracts for all tables

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | In Review |
| **Estimate** | 3 h |
| **Depends on** | [F02-T02](F02-T02-data-dictionary.md), [F02-T03](F02-T03-reference-data-sources.md) |
| **Branch** | `feat/F02-T04-data-contracts-odcs` |

## Description

Express schema, keys, quality rules, freshness SLA, ownership and classification for each table in ODCS v3 YAML.

## Steps

1. Define the ODCS subset used (fundamentals, schema, quality, SLA, team, tags) in `contracts/README.md`
2. Write the source contract (`sipni_doses`) and bronze contracts (all strings + metadata columns)
3. Write silver contracts (`vaccination_doses`, `quarantine_doses`, `late_arrivals`, `dim_establishment`)
4. Write gold contracts (dimensions, `fct_doses_daily`, indicators, `rt_doses_hourly`)
5. Flag `sensitive` / `quasi_identifier` columns

## Acceptance criteria

- [x] Contracts validate against the ODCS JSON schema
- [x] Every table in ARCHITECTURE §5.2 has a contract (except the event stream, F04-T01)

## Deliverables

- `contracts/README.md`
- `contracts/source/*.odcs.yaml`
- `contracts/bronze/*.odcs.yaml`
- `contracts/silver/*.odcs.yaml`
- `contracts/gold/*.odcs.yaml`
- `contracts/schema/odcs-json-schema-v3.2.0.json` (official, Apache-2.0)
- `scripts/validate_contracts.py`, `tests/unit/test_contracts_valid.py`

## Why this matters (best practice)

A data contract is an API for data: producers promise a shape and quality, consumers can build on it. ODCS is the vendor-neutral standard, so contracts are portable to catalog and quality tools.

## Notes

- Used **ODCS v3.2.0** (latest release, 2026-09-08). The official JSON Schema is vendored in `contracts/schema/` so validation works offline and is reproducible; `jsonschema` added as a dev dependency.
- **15 contracts**: 3 source (SI-PNI, IBGE, SINASC), 4 bronze (SI-PNI raw, IBGE, SINASC aggregated, seeds), 4 silver, 4 gold (dimensions and indicators grouped as several schema objects per file). The event-stream contract belongs to F04-T01.
- Source contracts are `active` v1.0.0 (they describe data that exists); lakehouse contracts are `proposed` v0.1.0 until each table is built.
- The SI-PNI source and bronze contracts were generated once from the data dictionary (56 columns, identical order); a test keeps bronze aligned with the source. The rest was scaffolded by a one-off script for consistent boilerplate and is edited by hand from now on.
- Column lineage is recorded with `transformSourceObjects`/`transformLogic`; the silver contract references exactly the 35 columns the data dictionary keeps (checked).
- Quality rules use the ODCS library metrics where they fit (nulls, duplicates, invalid values, row count) and SQL rules for cross-column/cross-table checks (registration after vaccination, reconciliation with silver, one current SCD2 version).
- Validator also enforces project conventions (id pattern, SemVer, layer property, primary keys in silver/gold); tested by tampering a contract (invalid `apiVersion` and `logicalType` were reported).
- Deliberate exception documented in the contract: SINASC is aggregated in bronze (privacy).
