# F08-T05 — Write the performance report

| Field | Value |
|---|---|
| **Feature** | [F08 — Partitioning, skew & performance](../features/F08-partitioning-skew-performance.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F08-T03](F08-T03-skew-mitigation.md), [F08-T04](F08-T04-file-layout-optimization.md) |
| **Branch** | `feat/F08-T05-performance-report` |

## Description

Consolidate experiments into a readable report with recommendations.

## Steps

1. Table of experiments: hypothesis, change, metric before/after
2. Physical plans (`explain`) for key queries
3. Recommendations for scaling to all 27 UFs

## Acceptance criteria

- [ ] Report reviewed; numbers reproducible from notebooks

## Deliverables

- `docs/performance.md`

## Why this matters (best practice)

Performance work without a write-up is lost the day you leave. Hypothesis → change → measurement is the scientific method applied to engineering.

## Notes

_Add decisions, problems found and links to the PR here while working._
