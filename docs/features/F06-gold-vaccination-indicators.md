# F06 — Gold layer — vaccination indicators

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F05](F05-silver-layer.md) |
| **Estimate** | 15.5 h |
| **Created** | 2026-11-25 |

## Goal

A star schema and official-style PNI indicators (coverage, dropout, homogeneity, timeliness) plus a near-real-time view, built incrementally from silver.

## User story

> As a municipal health manager, I want to see whether my municipality meets each vaccine target and registers doses on time, so that I can act and be held accountable.

## Scope

**In scope**

- Conformed dimensions and `fct_doses_daily`
- Incremental build from silver Change Data Feed
- Coverage, dropout, homogeneity, timeliness indicators
- Streaming hourly aggregate with watermark
- Small-cell suppression
- Reconciliation with the Ministry's official panel

**Out of scope**

- Forecasting / ML (later projects)
- Financial transfer data (possible future extension)

## Acceptance criteria

- [ ] Indicator methodology documented and cited
- [ ] Gold rebuild from scratch = incremental result (test)
- [ ] Coverage for a sample of municipalities reconciles with the official panel or the difference is explained
- [ ] No published cell below the suppression threshold

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F06-T01](../tasks/F06-T01-gold-dimensional-model.md) | Design the gold star schema | 2 h | To Do |
| [F06-T02](../tasks/F06-T02-incremental-gold-with-cdf.md) | Build gold incrementally from Change Data Feed | 3 h | To Do |
| [F06-T03](../tasks/F06-T03-coverage-indicator.md) | Compute vaccination coverage | 3 h | To Do |
| [F06-T04](../tasks/F06-T04-dropout-and-homogeneity.md) | Compute dropout and homogeneity | 2.5 h | To Do |
| [F06-T05](../tasks/F06-T05-timeliness-and-near-real-time.md) | Timeliness indicator and real-time hourly view | 3 h | To Do |
| [F06-T06](../tasks/F06-T06-reconciliation-with-official-panel.md) | Reconcile with official figures | 2 h | To Do |

## Syllabus topics covered

- Eng 1.1 Relational and multidimensional models; normalisation and integrity
- Eng 1.2 Data warehouse and data mart
- Eng 5.4 Reconciliation of sources
- Ops 3.1 Roles, risks and evidence about data and decisions

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
