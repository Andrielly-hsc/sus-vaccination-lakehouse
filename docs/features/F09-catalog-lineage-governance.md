# F09 — Catalog, lineage & governance

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Should (MoSCoW) |
| **Depends on** | [F06](F06-gold-vaccination-indicators.md) |
| **Estimate** | 10.5 h |
| **Created** | 2026-11-25 |

## Goal

A documented catalog of every table, automatic lineage from source files to indicators, an audit trail and governance documentation.

## User story

> As an auditor, I want to trace any published indicator back to its source files and see who changed what and when, so that the numbers can be independently verified.

## Scope

**In scope**

- Spark catalog registration with comments/properties from contracts
- OpenLineage events + generated lineage doc
- Generated catalog docs
- Delta history as audit trail, retention policy
- Data card, ownership, LGPD notes

**Out of scope**

- Running a catalog server permanently (Marquez optional)
- Access control enforcement (single-user local setup)

## Acceptance criteria

- [ ] All tables registered with descriptions for every column
- [ ] `docs/lineage.md` generated from OpenLineage events shows landing → gold
- [ ] Data card published
- [ ] Audit query shows the history of a gold table

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F09-T01](../tasks/F09-T01-metastore-catalog.md) | Register tables in the catalog | 2 h | To Do |
| [F09-T02](../tasks/F09-T02-openlineage-integration.md) | Capture lineage with OpenLineage | 3 h | To Do |
| [F09-T03](../tasks/F09-T03-data-catalog-docs.md) | Generate catalog documentation | 2 h | To Do |
| [F09-T04](../tasks/F09-T04-audit-and-time-travel.md) | Audit trail and retention | 1.5 h | To Do |
| [F09-T05](../tasks/F09-T05-data-card-and-governance.md) | Data card and governance roles | 2 h | To Do |

## Syllabus topics covered

- Eng 5.1 Metadata, catalogue and lineage
- Gov 6.5 Personal data protection and balance between utility and protection
- Ops 3.1 Roles, risks and evidence about data and decisions

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
