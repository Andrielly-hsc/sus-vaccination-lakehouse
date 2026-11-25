# F05 — Silver layer — cleaned, validated, conformed

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F03](F03-batch-ingestion-bronze.md), [F04](F04-streaming-simulation.md) |
| **Estimate** | 15.5 h |
| **Created** | 2026-11-25 |

## Goal

One trusted, deduplicated row per dose from both batch and stream paths, with invalid and too-late records quarantined instead of lost.

## User story

> As an analyst, I want a clean dose table with standard codes and no duplicates, so that every indicator is computed from the same trustworthy base.

## Scope

**In scope**

- Typing, renaming, code standardisation, municipality 6/7-digit conformance, minimisation
- Row-level validation with quarantine
- Deduplication and idempotent MERGE
- Streaming silver with watermark and late-arrival handling
- Establishment dimension with SCD Type 2

**Out of scope**

- Business aggregates (F06)

## Acceptance criteria

- [ ] `silver.vaccination_doses.dose_id` is unique
- [ ] bronze rows = silver rows + quarantined + duplicates removed (reconciled per run)
- [ ] Re-processing the same bronze data leaves silver unchanged (same Delta row count and content hash)
- [ ] Events beyond the watermark land in `silver.late_arrivals` and are later merged by the batch path

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F05-T01](../tasks/F05-T01-silver-transformations.md) | Implement silver transformations | 3 h | To Do |
| [F05-T02](../tasks/F05-T02-validation-and-quarantine.md) | Row validation and quarantine | 2 h | To Do |
| [F05-T03](../tasks/F05-T03-dedup-and-merge.md) | Deduplicate and MERGE into silver | 3 h | To Do |
| [F05-T04](../tasks/F05-T04-streaming-silver-with-watermark.md) | Streaming silver with watermark and late data | 3 h | To Do |
| [F05-T05](../tasks/F05-T05-establishment-dimension-scd2.md) | Establishment dimension with SCD Type 2 | 2.5 h | To Do |
| [F05-T06](../tasks/F05-T06-silver-tests.md) | Silver reconciliation tests | 2 h | To Do |

## Syllabus topics covered

- 5.1 Missing values, inconsistencies, duplicates, outliers
- Eng 5.3 Profiling, deduplication, record linkage, enrichment
- Eng 1.1 Transactions and consistency
- Gov 6.1 Minimisation · 6.3 Pseudonymisation

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
