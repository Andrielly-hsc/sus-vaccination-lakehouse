# F07-T01 — Set up Great Expectations

| Field | Value |
|---|---|
| **Feature** | [F07 — Data quality with Great Expectations](../features/F07-data-quality-great-expectations.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F05-T01](F05-T01-silver-transformations.md) |
| **Branch** | `feat/F07-T01-gx-setup` |

## Description

File-based GX context in the repo with a Spark DataFrame datasource.

## Steps

1. `gx/` file data context; Spark datasource and DataFrame assets per table
2. Thin wrapper `quality/gx_runner.py` isolating the GX API
3. Smoke test on a fixture table

## Acceptance criteria

- [ ] A suite runs from Python against a Delta table read with Spark

## Deliverables

- `gx/`
- `src/vaccination_lakehouse/quality/gx_runner.py`

## Why this matters (best practice)

Wrapping a fast-moving third-party API behind a small module keeps upgrades local — GX's 0.x → 1.x change showed how valuable that is.

## Notes

_Add decisions, problems found and links to the PR here while working._
