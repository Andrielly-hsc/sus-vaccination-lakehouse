# F04-T04 — Prove fault tolerance and exactly-once

| Field | Value |
|---|---|
| **Feature** | [F04 — Real-time feed simulation & streaming bronze](../features/F04-streaming-simulation.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F04-T03](F04-T03-streaming-bronze.md) |
| **Branch** | `feat/F04-T04-fault-tolerance` |

## Description

Demonstrate and document what happens on crash, restart and code changes.

## Steps

1. Test: stop the query mid-replay, restart, compare event counts with the replayer's log
2. Document checkpoint contents (offsets, commits, metadata) and the restart-compatibility rules
3. Runbook: when a new checkpoint is required and how to backfill safely

## Acceptance criteria

- [ ] Restart test passes: emitted = ingested, no duplicates by `event_id` beyond injected ones
- [ ] `docs/runbook.md` has a streaming section

## Deliverables

- `tests/integration/test_stream_restart.py`
- `docs/runbook.md (streaming section)`

## Why this matters (best practice)

Exactly-once is an end-to-end property (replayable source + checkpoint + idempotent sink). Engineers who can explain and prove it are trusted to run streams in production.

## Notes

_Add decisions, problems found and links to the PR here while working._
