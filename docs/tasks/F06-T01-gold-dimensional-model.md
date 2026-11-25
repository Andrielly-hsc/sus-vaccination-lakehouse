# F06-T01 — Design the gold star schema

| Field | Value |
|---|---|
| **Feature** | [F06 — Gold layer — vaccination indicators](../features/F06-gold-vaccination-indicators.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F05-T05](F05-T05-establishment-dimension-scd2.md) |
| **Branch** | `feat/F06-T01-gold-dimensional-model` |

## Description

Dimensions and the daily fact table, with grain, keys and contracts.

## Steps

1. Declare grain of `fct_doses_daily` (municipality × establishment × vaccine × dose × date)
2. `dim_municipality` (from IBGE, with region/UF), `dim_vaccine` (vaccine + dose + schedule role), `dim_date`, `dim_establishment` (SCD2 from silver)
3. Deterministic surrogate keys; unknown members (`-1`) for missing references
4. Update gold contracts and an ER diagram in ARCHITECTURE if changed

## Acceptance criteria

- [ ] Every fact row joins to every dimension (no orphan keys; unknown member used instead)

## Deliverables

- `src/vaccination_lakehouse/gold/model.py`
- `contracts/gold/*.odcs.yaml`

## Why this matters (best practice)

Kimball's 'declare the grain first' prevents the most expensive modelling mistake: facts that double-count when joined. Unknown members keep facts and reports consistent when references are missing.

## Notes

_Add decisions, problems found and links to the PR here while working._
