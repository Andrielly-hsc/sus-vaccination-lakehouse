# F11-T01 — Serving layer without Spark

| Field | Value |
|---|---|
| **Feature** | [F11 — Accountability dashboard](../features/F11-accountability-dashboard.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F06-T03](F06-T03-coverage-indicator.md) |
| **Branch** | `feat/F11-T01-serving-layer` |

## Description

Read gold Delta tables with delta-rs/DuckDB for fast, light queries.

## Steps

1. `dashboard/data.py` reading Delta via `deltalake` and querying with DuckDB
2. Caching with `st.cache_data`
3. Reconciliation script comparing dashboard queries with Spark results

## Acceptance criteria

- [ ] Reconciliation script passes in CI

## Deliverables

- `dashboard/data.py`
- `scripts/check_dashboard.py`

## Why this matters (best practice)

Consumers should not need a Spark cluster to read a few thousand rows. Open table formats let different engines read the same data — a key lakehouse promise.

## Notes

_Add decisions, problems found and links to the PR here while working._
