# F07-T02 — Write expectation suites per layer

| Field | Value |
|---|---|
| **Feature** | [F07 — Data quality with Great Expectations](../features/F07-data-quality-great-expectations.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F07-T01](F07-T01-gx-setup.md), [F02-T05](F02-T05-contract-loader-and-schema-generation.md) |
| **Branch** | `feat/F07-T02-expectation-suites` |

## Description

Generate suites from contracts and add hand-written expectations for business rules.

## Steps

1. Generator: contract → expectations (columns exist, types, not null, unique, allowed values, ranges)
2. Bronze: file completeness (row count vs manifest)
3. Silver: validity (dates, codes, ages), uniqueness (`dose_id`), field completeness thresholds
4. Gold: consistency (fact total = silver), non-negative indicators, freshness
5. Severity metadata (`critical` / `warning`) per expectation

## Acceptance criteria

- [ ] Each layer has a suite covering the three dimensions completeness, validity, uniqueness

## Deliverables

- `src/vaccination_lakehouse/quality/suites.py`
- `gx/expectations/`

## Why this matters (best practice)

Generating the obvious checks from contracts guarantees coverage; hand-written ones capture business knowledge. Severity levels prevent alert fatigue.

## Notes

_Add decisions, problems found and links to the PR here while working._
