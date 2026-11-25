# F02-T04 — Write ODCS contracts for all tables

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | To Do |
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

- [ ] Contracts validate against the ODCS JSON schema
- [ ] Every table in ARCHITECTURE §5.2 has a contract

## Deliverables

- `contracts/README.md`
- `contracts/source/*.odcs.yaml`
- `contracts/bronze/*.odcs.yaml`
- `contracts/silver/*.odcs.yaml`
- `contracts/gold/*.odcs.yaml`

## Why this matters (best practice)

A data contract is an API for data: producers promise a shape and quality, consumers can build on it. ODCS is the vendor-neutral standard, so contracts are portable to catalog and quality tools.

## Notes

_Add decisions, problems found and links to the PR here while working._
