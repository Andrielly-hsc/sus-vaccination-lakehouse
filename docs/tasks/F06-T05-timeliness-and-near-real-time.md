# F06-T05 — Timeliness indicator and real-time hourly view

| Field | Value |
|---|---|
| **Feature** | [F06 — Gold layer — vaccination indicators](../features/F06-gold-vaccination-indicators.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F06-T02](F06-T02-incremental-gold-with-cdf.md), [F05-T04](F05-T04-streaming-silver-with-watermark.md) |
| **Branch** | `feat/F06-T05-timeliness-and-near-real-time` |

## Description

Registration-lag indicator per municipality/facility, and a streaming hourly aggregate.

## Steps

1. `ind_timeliness_monthly`: p50/p90 lag, % registered within 7 and 30 days, per municipality and establishment
2. `rt_doses_hourly`: streaming `groupBy(window(event_time, '1 hour'), municipality, vaccine)` with watermark, append mode to Delta
3. Mark real-time numbers as provisional (`is_provisional`)
4. Tests with `availableNow`

## Acceptance criteria

- [ ] Hourly view updates during a replay
- [ ] Timeliness ranks facilities by p90 lag

## Deliverables

- `src/vaccination_lakehouse/gold/timeliness.py`
- `src/vaccination_lakehouse/gold/realtime.py`

## Why this matters (best practice)

Timeliness is both a data-quality and an accountability metric: late registration hides outbreaks and distorts coverage. Windowed streaming aggregates with watermarks are the canonical real-time pattern (IoT dashboards use exactly this).

## Notes

_Add decisions, problems found and links to the PR here while working._
