# F03-T03 — Load CSV extracts into bronze Delta

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | In Review |
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

- [x] Bronze row count = manifest rows for loaded files
- [x] Corrupt rows are counted and stored, not lost

## Deliverables

- `src/vaccination_lakehouse/ingestion/bronze_batch.py`
- `contracts/bronze/sipni_doses_raw.odcs.yaml (used)`

## Why this matters (best practice)

Bronze is the system of record inside the lakehouse. Keeping data as strings plus provenance columns means any later bug can be traced to the exact file and fixed by replaying — never by editing data by hand.

## Notes

- Bronze contract bumped to **0.2.0**: source columns became optional in bronze (bronze stores whatever arrives; requiredness is enforced in silver). The compatibility checker classified it as additive (minor) and accepted it.
- Real run: **2 748 844 rows, 0 corrupt**, reconciliation per file OK. Column comments and table properties come from the contract (`lakehouse.ensure_table`).
- Two performance problems found and fixed with measurements (docs/performance.md, experiments 1 and 2): the partitioned write's sort (fixed with `spark.sql.maxConcurrentOutputFileWriters`) and caching the micro-batch to list its files (replaced by a pre-flight check plus a manifest hash map). **14 min 28 s → 3 min 41 s** for one month.
