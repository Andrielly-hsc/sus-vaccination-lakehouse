# F05-T05 — Establishment dimension with SCD Type 2

| Field | Value |
|---|---|
| **Feature** | [F05 — Silver layer — cleaned, validated, conformed](../features/F05-silver-layer.md) |
| **Status** | To Do |
| **Estimate** | 2.5 h |
| **Depends on** | [F05-T03](F05-T03-dedup-and-merge.md) |
| **Branch** | `feat/F05-T05-establishment-dimension-scd2` |

## Description

Track changes of facility attributes (name, municipality, type) over time.

## Steps

1. Derive establishment attributes per `establishment_code` from silver doses (and CNES if available)
2. MERGE implementing SCD2: close the current row (`valid_to`, `is_current=false`), insert the new version
3. Deterministic surrogate key `establishment_sk`
4. Tests with a facility that changes name twice

## Acceptance criteria

- [ ] Exactly one current row per establishment
- [ ] History preserved and queryable as-of a date

## Deliverables

- `src/vaccination_lakehouse/silver/establishments.py`
- `tests/spark/test_scd2.py`

## Why this matters (best practice)

In IoT terms this is the *device registry*. SCD2 lets reports show facts with the attributes valid at the time — a standard Kimball technique and a frequent interview topic.

## Notes

_Add decisions, problems found and links to the PR here while working._
