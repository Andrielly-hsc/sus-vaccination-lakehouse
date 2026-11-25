# F03-T03 — Load CSV extracts into bronze Delta

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F03-T02](F03-T02-landing-zone-layout.md), [F02-T05](F02-T05-contract-loader-and-schema-generation.md) |
| **Branch** | `feat/F03-T03-bronze-batch-load` |

## Description

Read landing CSVs with the contract schema (all strings) and append them to `bronze.sipni_doses_raw`.

## Steps

1. Read with explicit schema from the bronze contract, `mode=PERMISSIVE` and `columnNameOfCorruptRecord`
2. Add `_ingested_at`, `_source_file` (`_metadata.file_path`), `_file_hash`, `_batch_id`, `_ingest_date`
3. Append to Delta partitioned by `_ingest_date`; table comments/properties from the contract
4. Corrupt records → `bronze.sipni_doses_corrupt` instead of failing the whole file

## Acceptance criteria

- [ ] Bronze row count = manifest rows for loaded files
- [ ] Corrupt rows are counted and stored, not lost

## Deliverables

- `src/vaccination_lakehouse/ingestion/bronze_batch.py`
- `contracts/bronze/sipni_doses_raw.odcs.yaml (used)`

## Why this matters (best practice)

Bronze is the system of record inside the lakehouse. Keeping data as strings plus provenance columns means any later bug can be traced to the exact file and fixed by replaying — never by editing data by hand.

## Notes

_Add decisions, problems found and links to the PR here while working._
