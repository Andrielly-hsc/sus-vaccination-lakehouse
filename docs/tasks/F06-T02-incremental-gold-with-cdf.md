# F06-T02 — Build gold incrementally from Change Data Feed

| Field | Value |
|---|---|
| **Feature** | [F06 — Gold layer — vaccination indicators](../features/F06-gold-vaccination-indicators.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F06-T01](F06-T01-gold-dimensional-model.md) |
| **Branch** | `feat/F06-T02-incremental-gold-with-cdf` |

## Description

Recompute only the partitions affected by silver changes since the last gold run.

## Steps

1. Read `table_changes` from the last processed silver version (stored in `ops.watermarks`)
2. Derive affected (month, municipality) keys; recompute those slices from silver
3. Write with `replaceWhere` (deterministic overwrite of affected slices)
4. Test: incremental result = full rebuild

## Acceptance criteria

- [ ] Second run with no silver changes does nothing
- [ ] Incremental = full rebuild (test)

## Deliverables

- `src/vaccination_lakehouse/gold/incremental.py`
- `tests/integration/test_gold_incremental.py`

## Why this matters (best practice)

Recomputing everything daily does not scale; appending aggregates double-counts late data. 'Find affected slices, recompute them deterministically' is the robust incremental pattern for aggregates.

## Notes

_Add decisions, problems found and links to the PR here while working._
