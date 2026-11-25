# F04-T03 — Stream events into bronze

| Field | Value |
|---|---|
| **Feature** | [F04 — Real-time feed simulation & streaming bronze](../features/F04-streaming-simulation.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F04-T02](F04-T02-event-replayer.md) |
| **Branch** | `feat/F04-T03-streaming-bronze` |

## Description

Structured Streaming query from the stream landing folder to `bronze.sipni_dose_events_raw`.

## Steps

1. `readStream.format('json')` with the contract schema, `maxFilesPerTrigger`
2. Add ingestion metadata; append to Delta with checkpoint `checkpoints/bronze_sipni_events`
3. Trigger `processingTime='10 seconds'` (live) or `availableNow` (tests)
4. CLI `vaxlake stream --layer bronze`

## Acceptance criteria

- [ ] Events appear in bronze within ~2 trigger intervals
- [ ] Integration test with `availableNow` passes

## Deliverables

- `src/vaccination_lakehouse/streaming/bronze_stream.py`
- `tests/integration/test_stream_bronze.py`

## Why this matters (best practice)

Bronze for streams follows the same rule as for batch: append raw, add provenance, no logic. Keeping the stream's first hop trivial makes it robust and replayable.

## Notes

_Add decisions, problems found and links to the PR here while working._
