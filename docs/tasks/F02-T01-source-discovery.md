# F02-T01 — Discover and document the SI-PNI source

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | To Do |
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

- [ ] `sources.md` contains URL, licence, format, size per month, encoding, columns and known caveats
- [ ] Event-time and processing-time columns identified

## Deliverables

- `docs/data/sources.md`
- `notebooks/01_source_exploration.ipynb`

## Why this matters (best practice)

Most pipeline bugs come from wrong assumptions about the source (encoding, delimiters, revised history). Documenting discovery turns tribal knowledge into an asset, and is the first step of any data-contract conversation with a producer.

## Notes

_Add decisions, problems found and links to the PR here while working._
