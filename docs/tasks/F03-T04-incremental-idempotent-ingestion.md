# F03-T04 — Make ingestion incremental and idempotent

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F03-T03](F03-T03-bronze-batch-load.md) |
| **Branch** | `feat/F03-T04-incremental-idempotent-ingestion` |

## Description

Use Structured Streaming's file source with `trigger(availableNow=True)` and a checkpoint so each file is processed exactly once.

## Steps

1. Wrap the bronze load in `readStream` (csv) → `writeStream` (delta) with checkpoint `checkpoints/bronze_sipni_batch`
2. `maxFilesPerTrigger` to bound memory; `availableNow` to stop when done
3. `--full-refresh`: drop table + checkpoint explicitly, with confirmation, and reload from landing
4. Log files processed per run in `ops.run_log` (prepared in F10)

## Acceptance criteria

- [ ] Second run: 0 new rows, 0 files processed
- [ ] A run killed mid-way and re-run produces no duplicates
- [ ] Full refresh rebuilds identical row counts

## Deliverables

- `src/vaccination_lakehouse/ingestion/bronze_batch.py`
- `docs/runbook.md (ingestion section)`

## Why this matters (best practice)

This is the 'Auto Loader' pattern: let the engine track which files were processed instead of hand-written bookkeeping. Idempotent re-runs are the single most important property of a production pipeline, because jobs *will* fail and be retried.

## Notes

_Add decisions, problems found and links to the PR here while working._
