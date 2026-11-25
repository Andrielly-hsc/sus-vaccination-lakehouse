# F04-T02 — Build the event replayer

| Field | Value |
|---|---|
| **Feature** | [F04 — Real-time feed simulation & streaming bronze](../features/F04-streaming-simulation.md) |
| **Status** | To Do |
| **Estimate** | 4 h |
| **Depends on** | [F04-T01](F04-T01-event-envelope-contract.md), [F03-T02](F03-T02-landing-zone-layout.md) |
| **Branch** | `feat/F04-T02-event-replayer` |

## Description

A CLI that replays landing records as a live event stream in accelerated event time.

## Steps

1. Read a month's extract; synthesise time of day within opening hours (documented assumption)
2. Emission time = event time + real registration lag (scaled by speed factor), so late data is authentic
3. Emit in emission-time order as small JSON-lines files (write temp → atomic rename) every N simulated minutes
4. Inject configurable duplicates and reordering; deterministic with `--seed`
5. CLI `vaxlake replay --month 2025-07 --speed 2880 --dup-rate 0.01`

## Acceptance criteria

- [ ] Same seed → identical files
- [ ] Lag distribution of emitted events matches the source distribution (test)
- [ ] No partially written file is ever visible

## Deliverables

- `src/vaccination_lakehouse/streaming/replayer.py`
- `tests/unit/test_replayer.py`

## Why this matters (best practice)

Simulations are only useful if they are realistic and reproducible. Deriving lateness from real registration lags avoids teaching the pipeline on an invented, too-friendly distribution.

## Notes

_Add decisions, problems found and links to the PR here while working._
