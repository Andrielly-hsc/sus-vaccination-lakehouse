# F03-T01 — Build a resumable, filtering downloader

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | To Do |
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

- [ ] Interrupted download can be re-run without corrupt files
- [ ] Memory stays bounded (no full-file load)
- [ ] Manifest records source URL, bytes, rows kept/total, sha256

## Deliverables

- `src/vaccination_lakehouse/ingestion/download.py`
- `tests/unit/test_download.py (mocked HTTP)`

## Why this matters (best practice)

Network calls fail; well-behaved clients retry with backoff and do not hammer public servers. Filtering while streaming keeps an 8 GB laptop viable — the same idea as predicate push-down, applied at the edge.

## Notes

_Add decisions, problems found and links to the PR here while working._
