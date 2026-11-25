# F05-T02 — Row validation and quarantine

| Field | Value |
|---|---|
| **Feature** | [F05 — Silver layer — cleaned, validated, conformed](../features/F05-silver-layer.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F05-T01](F05-T01-silver-transformations.md) |
| **Branch** | `feat/F05-T02-validation-and-quarantine` |

## Description

Apply contract rules row by row; route failures to `silver.quarantine_doses` with a reason.

## Steps

1. Generate rule expressions from the silver contract (not null, ranges, allowed values, date ≤ today)
2. Add `reject_reasons` array; split valid/invalid DataFrames
3. Write quarantine with original payload, reasons, `_batch_id`
4. Report counts per reason in the run log

## Acceptance criteria

- [ ] No row disappears: valid + quarantined = input
- [ ] Top reject reasons visible per run

## Deliverables

- `src/vaccination_lakehouse/silver/validate.py`
- `tests/spark/test_validate.py`

## Why this matters (best practice)

Dropping bad rows silently biases indicators; failing the whole job for one bad row stops reporting. Quarantine is the standard middle way: keep flowing, keep evidence, fix and replay.

## Notes

_Add decisions, problems found and links to the PR here while working._
