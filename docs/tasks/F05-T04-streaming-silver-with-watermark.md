# F05-T04 — Streaming silver with watermark and late data

| Field | Value |
|---|---|
| **Feature** | [F05 — Silver layer — cleaned, validated, conformed](../features/F05-silver-layer.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F05-T03](F05-T03-dedup-and-merge.md), [F04-T03](F04-T03-streaming-bronze.md) |
| **Branch** | `feat/F05-T04-streaming-silver-with-watermark` |

## Description

Bronze (batch + events) → silver as streaming queries, with an explicit late-data policy.

## Steps

1. Read bronze Delta tables as streams; union batch and event paths after transformation
2. `withWatermark('event_time', '<N> days')` + `dropDuplicatesWithinWatermark('dose_id')`
3. Events older than the watermark → `silver.late_arrivals`; batch path reconciles them into silver
4. Document the policy: real-time = provisional, batch = final

## Acceptance criteria

- [ ] Late events are never lost (test with a very late event)
- [ ] State size stays bounded during a long replay

## Deliverables

- `src/vaccination_lakehouse/silver/stream_silver.py`
- `docs/runbook.md (late data policy)`

## Why this matters (best practice)

Watermarks trade completeness for bounded state and latency. Making that trade explicit — and recovering what the stream drops — is what distinguishes a production design from a demo.

## Notes

_Add decisions, problems found and links to the PR here while working._
