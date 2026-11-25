# F08-T01 — Choose and justify partition strategies

| Field | Value |
|---|---|
| **Feature** | [F08 — Partitioning, skew & performance](../features/F08-partitioning-skew-performance.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F05-T03](F05-T03-dedup-and-merge.md) |
| **Branch** | `feat/F08-T01-partition-strategy` |

## Description

Decide partition columns per table from query patterns and data volume.

## Steps

1. List query patterns per table (filters, joins)
2. Measure sizes per candidate partition (month, UF, municipality)
3. Apply the rule of thumb (few, large partitions; low cardinality; filter column)
4. Record decision in an ADR

## Acceptance criteria

- [ ] ADR with measured partition sizes and file counts

## Deliverables

- `docs/adr/00xx-partitioning-strategy.md`
- `notebooks/05_partition_sizes.ipynb`

## Why this matters (best practice)

Partitioning is a physical design decision that is hard to undo. Choosing from measured query patterns — not habit — is what senior engineers do.

## Notes

_Add decisions, problems found and links to the PR here while working._
