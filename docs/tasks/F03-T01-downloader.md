# F03-T01 — Build a resumable, filtering downloader

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | In Review |
| **Estimate** | 3 h |
| **Depends on** | [F02-T01](F02-T01-source-discovery.md) |
| **Branch** | `feat/F03-T01-downloader` |

## Description

Download monthly national files, streaming them through a UF filter so only the scope reaches disk.

## Steps

1. HTTP streaming download with timeouts, retries + exponential backoff, generic User-Agent, rate limiting
2. Stream-decode the CSV (encoding from `sources.md`) and keep rows whose establishment UF is in scope; write gzip CSV extract
3. Skip months already in the manifest with a matching checksum; `--force` to redo
4. Write each file to a temp name, then rename atomically
5. CLI `vaxlake download --months 2024-01:2025-06`

## Acceptance criteria

- [x] Interrupted download can be re-run without corrupt files
- [x] Memory stays bounded (no full-file load)
- [x] Manifest records source URL, bytes, rows kept/total, sha256

## Deliverables

- `src/vaccination_lakehouse/ingestion/download.py`
- `tests/unit/test_download.py (mocked HTTP)`

## Why this matters (best practice)

Network calls fail; well-behaved clients retry with backoff and do not hammer public servers. Filtering while streaming keeps an 8 GB laptop viable — the same idea as predicate push-down, applied at the edge.

## Notes

- Real run (2026-11-27, Jan/2025): 1.82 GB ZIP downloaded and filtered in **14 min 40 s**; **12 062 476** national rows read, **2 748 844** kept for ES + SP (22.8 %; the F02 estimate was 22.5 %), 0 rows without a UF. Peak memory **52 MB**: the CSV is streamed out of the ZIP line by line and never extracted.
- Idempotency by HTTP `HEAD` + ETag + scope in the manifest; resume via `Range`; retries with exponential backoff and jitter; the header is checked against the source contract before anything is written (`SourceSchemaError`).
- Tested with an in-memory fake HTTP server (dropped connection + resume, transient errors, 404 not retried, re-published month, widened scope).
