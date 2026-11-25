# F08-T02 — Analyse data skew

| Field | Value |
|---|---|
| **Feature** | [F08 — Partitioning, skew & performance](../features/F08-partitioning-skew-performance.md) |
| **Status** | To Do |
| **Estimate** | 2.5 h |
| **Depends on** | [F08-T01](F08-T01-partition-strategy.md) |
| **Branch** | `feat/F08-T02-skew-analysis` |

## Description

Quantify skew and observe its effect on Spark stages.

## Steps

1. Distribution of doses by UF, municipality, establishment (Gini / top-k share)
2. Run a join/groupBy by municipality with AQE off; capture task-time distribution in the Spark UI
3. Write the 'bad layout' experiment: partition silver by UF and measure file sizes and query times

## Acceptance criteria

- [ ] Skew metrics and Spark UI screenshots in `docs/performance.md`

## Deliverables

- `docs/performance.md (skew section)`
- `notebooks/06_skew_analysis.ipynb`

## Why this matters (best practice)

You cannot fix what you have not measured. Reading the Spark UI (stages, tasks, shuffle sizes) is a core, often-missing skill.

## Notes

_Add decisions, problems found and links to the PR here while working._
