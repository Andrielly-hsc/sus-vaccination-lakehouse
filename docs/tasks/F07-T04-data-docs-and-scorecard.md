# F07-T04 — Data Docs and quality scorecard

| Field | Value |
|---|---|
| **Feature** | [F07 — Data quality with Great Expectations](../features/F07-data-quality-great-expectations.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F07-T03](F07-T03-quality-gates-in-pipeline.md) |
| **Branch** | `feat/F07-T04-data-docs-and-scorecard` |

## Description

Human-readable quality documentation and a trend of quality per dimension.

## Steps

1. Build GX Data Docs locally (not committed; screenshot in docs)
2. Scorecard: % passing per dimension × table × run; freshness of each table
3. `docs/quality.md` explaining dimensions, rules and current status

## Acceptance criteria

- [ ] Scorecard generated from `ops.quality_results`

## Deliverables

- `src/vaccination_lakehouse/quality/scorecard.py`
- `docs/quality.md`

## Why this matters (best practice)

Quality you cannot see is quality nobody manages. Trends show whether a source is degrading before users complain.

## Notes

_Add decisions, problems found and links to the PR here while working._
