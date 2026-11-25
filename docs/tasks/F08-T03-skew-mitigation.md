# F08-T03 — Mitigate skew

| Field | Value |
|---|---|
| **Feature** | [F08 — Partitioning, skew & performance](../features/F08-partitioning-skew-performance.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F08-T02](F08-T02-skew-analysis.md) |
| **Branch** | `feat/F08-T03-skew-mitigation` |

## Description

Apply and compare AQE skew handling, broadcast joins and salting.

## Steps

1. Enable AQE skew join; measure
2. Broadcast small dimensions explicitly; check plan with `explain('formatted')`
3. Implement salting for a hot-key aggregation; compare
4. Keep the simplest technique that works; document

## Acceptance criteria

- [ ] Max/median task time ratio reduced and documented
- [ ] Chosen technique applied in the pipeline code

## Deliverables

- `src/vaccination_lakehouse/ops/skew.py (if needed)`
- `docs/performance.md (mitigation section)`

## Why this matters (best practice)

Skew is the most common reason a Spark job that 'should take minutes' takes hours. Knowing the ladder AQE → broadcast → salting, and when each applies, is a standard interview topic.

## Notes

_Add decisions, problems found and links to the PR here while working._
