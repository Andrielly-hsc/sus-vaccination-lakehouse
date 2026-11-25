# F02-T03 — Identify reference data and PNI targets

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | In Review |
| **Estimate** | 2 h |
| **Depends on** | [F02-T01](F02-T01-source-discovery.md) |
| **Branch** | `feat/F02-T03-reference-data-sources` |

## Description

Define the reference datasets needed to compute indicators and conform codes.

## Steps

1. IBGE municipality table (7-digit code, name, UF, region); document the 6 vs 7-digit DATASUS/IBGE rule
2. SINASC live births by municipality of residence and year (denominator for children < 1 and 1 year)
3. PNI targets per vaccine and which dose completes each schedule, from the Ministry's technical notes → `seeds/coverage_indicators.csv` with source citation
4. Vaccine and dose code tables (`seeds/vaccines.csv`, `seeds/doses.csv`)

## Acceptance criteria

- [x] Each reference source documented in `sources.md` with URL and vintage
- [x] `coverage_indicators.csv` cites the document for every value (`seeds/README.md`)

## Deliverables

- `docs/data/sources.md (reference section)`
- `seeds/coverage_indicators.csv`, `seeds/vaccines.csv`, `seeds/doses.csv`, `seeds/README.md`
- `scripts/discovery/build_code_seeds.py`

## Why this matters (best practice)

Indicators are only as good as their denominators and thresholds. Versioning small reference tables with citations ("seeds") makes every target auditable — essential for accountability reporting.

## Notes

- **Key discovery:** since 2024 the Ministry computes coverage per **individual**, not per dose (Nota Técnica 90/2025-DPNI, which revokes NT 117/2024). The open data has the pseudonymous `co_paciente`, so the official method can be reproduced; the data dictionary now records `patient_key` as required.
- IBGE localities API: 5 571 municipalities; the 6-digit SI-PNI code is the IBGE code without its check digit and is unique; all facility codes in the samples match.
- SINASC: yearly ZIPs on S3 (2024 final, 2025 preliminary). Microdata describes births and mothers, so ingestion will aggregate to counts per municipality and year (minimisation).
- Seeds renamed from the plan (`pni_targets`, `vaccine_dose_map`) to `coverage_indicators.csv`, `vaccines.csv` and `doses.csv`, with provenance in `seeds/README.md`; references in other tasks updated.
- **Open point:** no Ministry document with every target in one table was found; targets come from the CNM 2026 study citing the national calendar (secondary source). To be checked in F06-T06.
- Hepatitis B at birth (≤ 30 days) is marked not computable: the file has age in whole years only.
- The two PDFs could not be read by the web-fetch tool; they were downloaded and read locally (pypdf in a scratch folder).
