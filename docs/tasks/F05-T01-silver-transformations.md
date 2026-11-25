# F05-T01 — Implement silver transformations

| Field | Value |
|---|---|
| **Feature** | [F05 — Silver layer — cleaned, validated, conformed](../features/F05-silver-layer.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F03-T03](F03-T03-bronze-batch-load.md), [F02-T05](F02-T05-contract-loader-and-schema-generation.md) |
| **Branch** | `feat/F05-T01-silver-transformations` |

## Description

Pure, tested functions that turn raw strings into typed, standardised, minimised columns.

## Steps

1. `rename_to_english`, `cast_types` (dates with explicit formats), `trim_and_nullify`
2. `standardise_municipality` (6/7 digits), `standardise_vaccine_and_dose` (map to `vaccine_dose_map`)
3. `add_registration_lag` (days between vaccination and registration)
4. `minimise` (birth date → age in months, drop fields marked *drop* in the dictionary)
5. Compose with `DataFrame.transform`; unit tests per function

## Acceptance criteria

- [ ] Every function has a Spark test with edge cases (nulls, garbage, boundary dates)

## Deliverables

- `src/vaccination_lakehouse/silver/transforms.py`
- `tests/spark/test_silver_transforms.py`

## Why this matters (best practice)

Small pure transforms are the PySpark equivalent of clean functions: easy to test, reuse and reason about. Minimising at the first typed layer means sensitive detail never spreads further.

## Notes

_Add decisions, problems found and links to the PR here while working._
