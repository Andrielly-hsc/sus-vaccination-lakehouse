# F08-T04 — Optimise file layout (compaction, clustering, vacuum)

| Field | Value |
|---|---|
| **Feature** | [F08 — Partitioning, skew & performance](../features/F08-partitioning-skew-performance.md) |
| **Status** | To Do |
| **Estimate** | 2.5 h |
| **Depends on** | [F08-T01](F08-T01-partition-strategy.md), [F04-T03](F04-T03-streaming-bronze.md) |
| **Branch** | `feat/F08-T04-file-layout-optimization` |

## Description

Fix the small-file problem created by streaming and improve data skipping.

## Steps

1. Measure file count/size of streaming tables after a replay
2. `OPTIMIZE` (compaction) and `ZORDER BY (municipality_code_6, vaccine_code)`; compare with liquid clustering
3. Check data skipping (files read) for typical filters
4. `VACUUM` with ≥ 7-day retention; `vaxlake optimize` command

## Acceptance criteria

- [ ] Files read for a municipality query reduced and documented
- [ ] Maintenance command idempotent

## Deliverables

- `src/vaccination_lakehouse/ops/maintenance.py`
- `docs/performance.md (file layout section)`

## Why this matters (best practice)

Streaming writes thousands of tiny files; each costs a file open and metadata. Compaction and clustering are routine maintenance on every Delta platform (Fabric and Databricks schedule them).

## Notes

_Add decisions, problems found and links to the PR here while working._
