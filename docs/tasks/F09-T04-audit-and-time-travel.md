# F09-T04 — Audit trail and retention

| Field | Value |
|---|---|
| **Feature** | [F09 — Catalog, lineage & governance](../features/F09-catalog-lineage-governance.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F09-T01](F09-T01-metastore-catalog.md) |
| **Branch** | `feat/F09-T04-audit-and-time-travel` |

## Description

Use Delta history and time travel for audit, and define retention.

## Steps

1. `vaxlake audit <table>`: summarise `DESCRIBE HISTORY` (operation, metrics, user, time)
2. Demonstrate `VERSION AS OF` reproduction of a past indicator and `RESTORE`
3. Retention policy doc: log retention, `VACUUM` retention, checkpoint retention

## Acceptance criteria

- [ ] Past indicator reproduced exactly from an older version

## Deliverables

- `src/vaccination_lakehouse/governance/audit.py`
- `docs/runbook.md (retention section)`

## Why this matters (best practice)

Accountability requires reproducing what was published on a date. Delta's transaction log gives this almost for free — if retention is designed, not left to defaults.

## Notes

_Add decisions, problems found and links to the PR here while working._
