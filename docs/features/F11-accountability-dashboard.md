# F11 — Accountability dashboard

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Should (MoSCoW) |
| **Depends on** | [F06](F06-gold-vaccination-indicators.md) |
| **Estimate** | 7 h |
| **Created** | 2026-11-25 |

## Goal

A lightweight dashboard reading gold tables that shows coverage vs targets, dropout, timeliness and the near-real-time feed, with honest caveats.

## User story

> As a citizen or council member, I want to see whether my municipality meets its vaccination targets and registers doses on time, so that I can hold managers accountable.

## Scope

**In scope**

- Serving gold via delta-rs + DuckDB (no Spark)
- Streamlit app with filters (UF, municipality, vaccine, year)
- Coverage vs target, dropout class, timeliness ranking, real-time panel
- Methodology and caveats on screen

**Out of scope**

- Hosting/public deployment (optional Streamlit Community Cloud)
- Power BI version (could be added later)

## Acceptance criteria

- [ ] Dashboard numbers reconcile with gold tables (automated check)
- [ ] Suppressed cells shown as suppressed, never as zero
- [ ] Provisional real-time numbers labelled as such

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F11-T01](../tasks/F11-T01-serving-layer.md) | Serving layer without Spark | 1.5 h | To Do |
| [F11-T02](../tasks/F11-T02-streamlit-dashboard.md) | Build the Streamlit dashboard | 4 h | To Do |
| [F11-T03](../tasks/F11-T03-indicator-communication.md) | Communicate methodology and uncertainty | 1.5 h | To Do |

## Syllabus topics covered

- Ops 4.6 Communicating results and uncertainty to users
- 1.1 Exploration and visualisation

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
