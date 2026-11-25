# F08 — Partitioning, skew & performance

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F05](F05-silver-layer.md), [F06](F06-gold-vaccination-indicators.md) |
| **Estimate** | 11.5 h |
| **Created** | 2026-11-25 |

## Goal

Evidence-based choices for partitioning, skew handling and file layout, measured with the Spark UI and documented with numbers.

## User story

> As a platform engineer, I want tables laid out so that typical queries read little data and no task becomes a straggler, so that the pipeline scales with more states.

## Scope

**In scope**

- Partition strategy per table
- Skew analysis (UF, municipality, establishment)
- AQE, broadcast joins, salting
- Small-file compaction, Z-ORDER vs liquid clustering, VACUUM
- Performance report

**Out of scope**

- Cluster sizing in the cloud
- Cost optimisation of a managed platform

## Acceptance criteria

- [ ] `docs/performance.md` shows before/after numbers for each optimisation
- [ ] A deliberately bad layout (partition by UF/municipality) is measured and rejected
- [ ] Skewed stage straggler reduced (max/median task time) with a documented technique
- [ ] Streaming tables are compacted on a schedule

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F08-T01](../tasks/F08-T01-partition-strategy.md) | Choose and justify partition strategies | 2 h | To Do |
| [F08-T02](../tasks/F08-T02-skew-analysis.md) | Analyse data skew | 2.5 h | To Do |
| [F08-T03](../tasks/F08-T03-skew-mitigation.md) | Mitigate skew | 3 h | To Do |
| [F08-T04](../tasks/F08-T04-file-layout-optimization.md) | Optimise file layout (compaction, clustering, vacuum) | 2.5 h | To Do |
| [F08-T05](../tasks/F08-T05-performance-report.md) | Write the performance report | 1.5 h | To Do |

## Syllabus topics covered

- Eng 2.2 Indexes, execution plans and performance; nulls, duplicates, misinterpretation errors
- Eng 3.1 Formats CSV, JSON, Parquet
- 5.1 Outliers and imbalance

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
