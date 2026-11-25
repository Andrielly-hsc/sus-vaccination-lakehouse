# F10-T03 — Run log and observability

| Field | Value |
|---|---|
| **Feature** | [F10 — Pipeline orchestration & operations](../features/F10-orchestration-and-operations.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F10-T01](F10-T01-cli-pipeline.md) |
| **Branch** | `feat/F10-T03-run-log-and-observability` |

## Description

Structured record of each step run for troubleshooting and reconciliation.

## Steps

1. `ops.run_log`: run_id, step, started/ended, status, rows_in, rows_out, rows_quarantined, error
2. Context manager `track_step()` used by every command
3. Summary command `vaxlake runs --last 10`

## Acceptance criteria

- [ ] Failed steps recorded with error message
- [ ] Row reconciliation visible per run

## Deliverables

- `src/vaccination_lakehouse/ops/run_log.py`

## Why this matters (best practice)

Observability (logs, metrics, run metadata) turns '3 a.m. what happened?' into a query. Rows in/out per step make silent data loss visible.

## Notes

_Add decisions, problems found and links to the PR here while working._
