# F10-T02 — Backfill and reprocessing

| Field | Value |
|---|---|
| **Feature** | [F10 — Pipeline orchestration & operations](../features/F10-orchestration-and-operations.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F10-T01](F10-T01-cli-pipeline.md) |
| **Branch** | `feat/F10-T02-backfill-and-reprocessing` |

## Description

Safe procedures to load new historical months and rebuild a layer from the one below.

## Steps

1. `vaxlake backfill --months …` (download + ingest + downstream)
2. `vaxlake rebuild --layer silver|gold` with explicit confirmation
3. Runbook scenarios: source revised a month; contract changed; corrupted table

## Acceptance criteria

- [ ] Each runbook scenario tested at least once on fixtures

## Deliverables

- `docs/runbook.md (operations section)`

## Why this matters (best practice)

Sources revise history and bugs get fixed; being able to reprocess a slice safely is a core operational capability of a medallion architecture.

## Notes

_Add decisions, problems found and links to the PR here while working._
