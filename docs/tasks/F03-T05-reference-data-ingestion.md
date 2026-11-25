# F03-T05 — Ingest reference data

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F02-T03](F02-T03-reference-data-sources.md), [F03-T02](F03-T02-landing-zone-layout.md) |
| **Branch** | `feat/F03-T05-reference-data-ingestion` |

## Description

Load IBGE municipalities, SINASC live births and seed tables into `bronze.ref_*`.

## Steps

1. Downloader adapters for IBGE and SINASC (or documented manual download if no stable API)
2. Seeds (`coverage_indicators`, `vaccines`, `doses`) loaded from `seeds/`
3. Overwrite by vintage with `replaceWhere` so re-runs are idempotent
4. Record vintage and source in table properties

## Acceptance criteria

- [ ] Each `bronze.ref_*` table has a vintage column and a contract
- [ ] Re-run does not duplicate rows

## Deliverables

- `src/vaccination_lakehouse/ingestion/reference.py`

## Why this matters (best practice)

Reference data changes slowly but does change (new municipalities, revised births). Keeping vintages explicit allows reproducing an indicator 'as published' on a given date.

## Notes

_Add decisions, problems found and links to the PR here while working._
