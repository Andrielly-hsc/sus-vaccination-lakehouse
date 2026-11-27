# F03 — Batch ingestion into bronze

| Field | Value |
|---|---|
| **Status** | In Review |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F02](F02-source-discovery-and-data-contracts.md) |
| **Estimate** | 14 h |
| **Created** | 2026-11-25 |

## Goal

Load historical SI-PNI months and reference data into bronze Delta tables incrementally, idempotently and with full traceability.

## User story

> As a data engineer, I want every source file loaded exactly once with its metadata, so that I can re-run, audit and rebuild any downstream number.

## Scope

**In scope**

- Polite, resumable downloader filtering national files to the configured UFs
- Immutable landing zone with a manifest
- Bronze batch load with contract schema and metadata columns
- Incremental ingestion with Structured Streaming `availableNow` + checkpoint
- Reference data ingestion
- Bad-record handling and reconciliation

**Out of scope**

- Streaming events (F04)
- Any cleaning or typing (F05)

## Acceptance criteria

- [x] Running `vaxlake ingest` twice adds 0 rows the second time
- [x] Every bronze row has `_ingested_at`, `_source_file`, `_file_hash`, `_batch_id`
- [x] Row counts reconcile: landing manifest = bronze rows per file
- [x] Malformed rows are kept in `_corrupt_record` and reported without blocking the load; a landing file **modified after landing** deliberately stops the run before anything is written (unverifiable data never reaches bronze) — criterion refined during implementation

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F03-T01](../tasks/F03-T01-downloader.md) | Build a resumable, filtering downloader | 3 h | In Review |
| [F03-T02](../tasks/F03-T02-landing-zone-layout.md) | Define the landing zone and manifest | 1 h | In Review |
| [F03-T03](../tasks/F03-T03-bronze-batch-load.md) | Load CSV extracts into bronze Delta | 3 h | In Review |
| [F03-T04](../tasks/F03-T04-incremental-idempotent-ingestion.md) | Make ingestion incremental and idempotent | 3 h | In Review |
| [F03-T05](../tasks/F03-T05-reference-data-ingestion.md) | Ingest reference data | 2 h | In Review |
| [F03-T06](../tasks/F03-T06-ingestion-tests.md) | Test the ingestion layer | 2 h | In Review |

## Syllabus topics covered

- Eng 3.1 ETL/ELT; batch, full and incremental; formats; failures, reprocessing and consistency
- Eng 1.1 Transactions and consistency
- 4.1 Python files and exceptions

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
