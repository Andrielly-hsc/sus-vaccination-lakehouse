# F03-T05 — Ingest reference data

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | In Review |
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

- [x] Each `bronze.ref_*` table has a vintage column and a contract
- [x] Re-run does not duplicate rows

## Deliverables

- `src/vaccination_lakehouse/ingestion/reference.py`

## Why this matters (best practice)

Reference data changes slowly but does change (new municipalities, revised births). Keeping vintages explicit allows reproducing an indicator 'as published' on a given date.

## Notes

- Real run: **IBGE 5 571** municipalities; **SINASC 2024: 2 389 325** live births (matches the ~2.38 million reported by IBGE and the Ministry of Health for 2024); **SINASC 2025 (preliminary): 2 456 688** — no public figure to compare yet, to check in F06-T06. Seeds: 15 indicators, 80 vaccines, 49 doses. 4 min 29 s in total.
- SINASC uses `UF0000` codes for an unknown municipality within a UF (13–14 codes, ~55 births a year): kept, treated as unknown in gold.
- SINASC is aggregated while streaming the ZIP; the landing file has only `birth_year, residence_municipality_code, live_births` (privacy rule P5, tested).
