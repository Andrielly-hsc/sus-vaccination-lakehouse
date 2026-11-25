# F10 — Pipeline orchestration & operations

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F06](F06-gold-vaccination-indicators.md), [F07](F07-data-quality-great-expectations.md) |
| **Estimate** | 8.5 h |
| **Created** | 2026-11-25 |

## Goal

One CLI that runs, backfills and reprocesses the whole pipeline, with run logs and an end-to-end CI job.

## User story

> As an operator, I want to run, re-run and backfill the pipeline with single commands and see what each run did, so that operating it does not require reading the code.

## Scope

**In scope**

- Typer CLI for all steps and `run-all`
- Backfill and layer rebuild
- Run log and structured logs
- End-to-end CI on fixtures
- Runbook

**Out of scope**

- A scheduler/orchestrator server (Airflow, Dagster) — discussed as next step

## Acceptance criteria

- [ ] `vaxlake run-all` runs landing → gold on fixtures from an empty folder
- [ ] Every step writes a row to `ops.run_log` with rows in/out and duration
- [ ] CI end-to-end job runs the pipeline twice and asserts identical gold tables

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F10-T01](../tasks/F10-T01-cli-pipeline.md) | CLI for every pipeline step | 2.5 h | To Do |
| [F10-T02](../tasks/F10-T02-backfill-and-reprocessing.md) | Backfill and reprocessing | 2 h | To Do |
| [F10-T03](../tasks/F10-T03-run-log-and-observability.md) | Run log and observability | 2 h | To Do |
| [F10-T04](../tasks/F10-T04-end-to-end-ci.md) | End-to-end CI job | 2 h | To Do |

## Syllabus topics covered

- Ops 1.3 Pipelines, tests, CI/CD · 1.4 Reproducibility
- Eng 3.1 ETL/ELT; batch, full and incremental; formats; failures, reprocessing and consistency

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
