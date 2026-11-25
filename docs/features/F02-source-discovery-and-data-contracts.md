# F02 — Source discovery & data contracts

| Field | Value |
|---|---|
| **Status** | In Progress |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F01](F01-project-setup.md) |
| **Estimate** | 16 h |
| **Created** | 2026-11-25 |

## Goal

Understand the public sources precisely and write machine-readable data contracts that every layer, test and document is generated from.

## User story

> As a data consumer, I want a contract stating the schema, meaning and quality guarantees of each table, so that I can trust and correctly interpret the indicators.

## Scope

**In scope**

- OpenDataSUS SI-PNI file discovery (URLs, sizes, encoding, delimiter, columns, update cadence)
- Data dictionary Portuguese → English
- Reference sources: IBGE, SINASC, PNI targets
- ODCS v3 contracts for source, bronze, silver and gold tables
- Contract loader → Spark schema; SemVer breaking-change check
- LGPD privacy assessment

**Out of scope**

- Automatic schema inference from source files
- Legal advice — the assessment is technical

## Acceptance criteria

- [ ] `docs/data/sources.md` lists every source with URL, licence, format and caveats
- [ ] Every table in ARCHITECTURE §5.2 has a contract in `contracts/`
- [ ] Spark schemas in code come only from contracts (no hand-written `StructType` for these tables)
- [ ] CI fails when a contract change is breaking without a major version bump

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F02-T01](../tasks/F02-T01-source-discovery.md) | Discover and document the SI-PNI source | 3 h | In Review |
| [F02-T02](../tasks/F02-T02-data-dictionary.md) | Write the data dictionary | 3 h | In Review |
| [F02-T03](../tasks/F02-T03-reference-data-sources.md) | Identify reference data and PNI targets | 2 h | In Review |
| [F02-T04](../tasks/F02-T04-data-contracts-odcs.md) | Write ODCS contracts for all tables | 3 h | To Do |
| [F02-T05](../tasks/F02-T05-contract-loader-and-schema-generation.md) | Generate Spark schemas from contracts | 3 h | To Do |
| [F02-T06](../tasks/F02-T06-privacy-assessment.md) | LGPD privacy assessment | 2 h | To Do |

## Syllabus topics covered

- Eng 5.1 Metadata, catalogue and lineage
- Eng 3.1 Formats CSV, JSON, Parquet
- Gov 6.1 Minimisation · 6.3 Pseudonymisation
- Gov 6.5 Personal data protection and balance between utility and protection

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
