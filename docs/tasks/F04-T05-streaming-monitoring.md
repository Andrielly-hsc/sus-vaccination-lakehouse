# F04-T05 — Monitor streaming queries

| Field | Value |
|---|---|
| **Feature** | [F04 — Real-time feed simulation & streaming bronze](../features/F04-streaming-simulation.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F04-T03](F04-T03-streaming-bronze.md) |
| **Branch** | `feat/F04-T05-streaming-monitoring` |

## Description

A `StreamingQueryListener` that records progress metrics for every micro-batch.

## Steps

1. Implement `onQueryProgress`: batch id, input rows, input/processing rate, batch duration, watermark, state rows
2. Write metrics as JSON logs and to `ops.stream_metrics` (Delta)
3. Notebook/plot: end-to-end latency (`_ingested_at − emitted_at`) during a replay

## Acceptance criteria

- [ ] Metrics recorded for every batch of a replay
- [ ] Latency chart in `docs/performance.md`

## Deliverables

- `src/vaccination_lakehouse/streaming/listeners.py`
- `docs/performance.md (streaming section)`

## Why this matters (best practice)

A stream nobody watches is a silent failure waiting to happen. Processing rate below input rate is the first sign of backlog; these metrics are what dashboards and alerts are built on.

## Notes

_Add decisions, problems found and links to the PR here while working._
