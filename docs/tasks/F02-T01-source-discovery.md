# F02-T01 — Discover and document the SI-PNI source

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | In Review |
| **Estimate** | 3 h |
| **Depends on** | [F01-T05](F01-T05-spark-session-and-config.md) |
| **Branch** | `feat/F02-T01-source-discovery` |

## Description

Find the official OpenDataSUS dataset for routine vaccination doses applied and document exactly how it is published.

## Steps

1. Locate the dataset on OpenDataSUS (dadosabertos.saude.gov.br / opendatasus.saude.gov.br); record dataset page, resource URLs and licence
2. Download **one** month and measure size, encoding (UTF-8 vs Latin-1), delimiter, quoting, header, row count
3. List all columns with sample values; identify event time (vaccination date) and processing time (registration/import date) columns
4. Check the publication cadence and whether past months are revised (affects incremental design)
5. Write `docs/data/sources.md`; keep a 1 000-row *anonymised-by-design* sample only locally (never committed)

## Acceptance criteria

- [x] `sources.md` contains URL, licence, format, size per month, encoding, columns and known caveats
- [x] Event-time and processing-time columns identified

## Deliverables

- `docs/data/sources.md`
- `scripts/discovery/remote_zip_sample.py` (HTTP Range sampler)
- `scripts/discovery/profile_sample.py` (format, columns, lag)

## Why this matters (best practice)

Most pipeline bugs come from wrong assumptions about the source (encoding, delimiters, revised history). Documenting discovery turns tribal knowledge into an asset, and is the first step of any data-contract conversation with a producer.

## Notes

- The portal moved to `dadosabertos.saude.gov.br` (Next.js); the old CKAN API is gone. Dataset metadata and resource URLs were read from the page's embedded JSON.
- **No full download was needed.** The files are ZIPs on S3, which accepts HTTP `Range` requests, so reading the ZIP directory plus the first ~8 MB gave the header, the encoding and 50 000 sample rows. Exact row counts come later from the downloader's manifest (F03-T01). This replaced the planned notebook with two reusable scripts.
- Sizes are larger than assumed in ADR-0003 (1.5-3.1 GB zipped, 6-12 GB of CSV per month); a note was added to the ADR.
- Key findings: Latin-1 + `;`; 56 columns stable from 2024 to 2026; the PDF dictionary does not match the CSV (8 renamed, 4 missing fields); `co_troca_documento` gives the source **update semantics**; registration lag median **31 days** (p90 58, max 583); past months are re-published.
- Risk raised: drive C: has 12 GB free and holds the WSL virtual disk; moving the distribution to D: is documented in `docs/setup.md` §1.7. **Resolved on 2026-11-25:** `ext4.vhdx` moved to `D:\WSL\Ubuntu-24.04` (321 GB free); the 25 tests and the smoke test pass after the move.
