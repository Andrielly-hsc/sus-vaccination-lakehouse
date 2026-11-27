# F03-T02 — Define the landing zone and manifest

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | In Review |
| **Estimate** | 1 h |
| **Depends on** | [F03-T01](F03-T01-downloader.md) |
| **Branch** | `feat/F03-T02-landing-zone-layout` |

## Description

A predictable, immutable folder layout with a manifest describing every file.

## Steps

1. Layout `landing/sipni/batch/vaccination_month=YYYY-MM/part-*.csv.gz`, `landing/reference/<name>/<vintage>/`
2. `_manifest.jsonl`: file, source URL, sha256, rows, downloaded_at, scope
3. Make landing read-only for the pipeline (only the downloader writes)

## Acceptance criteria

- [x] Manifest and files agree (checked by a test)

## Deliverables

- `src/vaccination_lakehouse/ingestion/landing.py`
- `docs/data/sources.md (layout section)`

## Why this matters (best practice)

An immutable landing zone is the safety net of a lakehouse: if every downstream table is lost, it can be rebuilt from landing. Manifests make completeness checkable.

## Notes

- Implemented together with T01 (branch `feat/F03-T01-T02-downloader-and-landing`): the downloader is the only writer of the landing zone.
- Parts of 500 000 rows (`ingestion.rows_per_file`) because gzip is not splittable: Jan/2025 → 1 ES part + 5 SP parts, 362 MB. The source ETag is in every file name, so a re-published month lands beside the old one (immutability).
- Atomic writes: hidden `.name.tmp` then `os.replace`; Spark's file source ignores names starting with `.` or `_`, so `_manifest.jsonl` and temporary files are never read as data. gzip `mtime=0` makes parts byte-reproducible.
