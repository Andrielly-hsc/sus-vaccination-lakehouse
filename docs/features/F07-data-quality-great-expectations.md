# F07 — Data quality with Great Expectations

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F05](F05-silver-layer.md) |
| **Estimate** | 11 h |
| **Created** | 2026-11-25 |

## Goal

Automated completeness, validity, uniqueness, consistency and timeliness checks at every layer, acting as gates in the pipeline and documented in Data Docs.

## User story

> As a data steward, I want the pipeline to stop when critical quality rules fail and to report warnings over time, so that bad data never reaches published indicators.

## Scope

**In scope**

- GX Core 1.x project with Spark DataFrame datasource
- Suites per layer generated from contracts
- Quality gates (critical blocks, warning logs)
- Results history and scorecard
- Data Docs
- Delta CHECK constraints

**Out of scope**

- Anomaly detection with ML
- Alerting integrations (e-mail/Slack) — logged only

## Acceptance criteria

- [ ] Completeness, validity and uniqueness expectations exist for bronze, silver and gold
- [ ] A critical failure stops the downstream write (tested)
- [ ] Results are stored in `ops.quality_results` and summarised in a scorecard
- [ ] Data Docs build locally

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F07-T01](../tasks/F07-T01-gx-setup.md) | Set up Great Expectations | 1.5 h | To Do |
| [F07-T02](../tasks/F07-T02-expectation-suites.md) | Write expectation suites per layer | 3 h | To Do |
| [F07-T03](../tasks/F07-T03-quality-gates-in-pipeline.md) | Run quality gates inside the pipeline | 3 h | To Do |
| [F07-T04](../tasks/F07-T04-data-docs-and-scorecard.md) | Data Docs and quality scorecard | 2 h | To Do |
| [F07-T05](../tasks/F07-T05-quality-tests.md) | Test the quality gates | 1.5 h | To Do |

## Syllabus topics covered

- Eng 5.2 Completeness, consistency, validity, uniqueness, accuracy, timeliness
- Eng 5.3 Profiling, deduplication, record linkage, enrichment
- Ops 1.3 Pipelines, tests, CI/CD

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
