# F02-T03 — Identify reference data and PNI targets

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F02-T01](F02-T01-source-discovery.md) |
| **Branch** | `feat/F02-T03-reference-data-sources` |

## Description

Define the reference datasets needed to compute indicators and conform codes.

## Steps

1. IBGE municipality table (7-digit code, name, UF, region); document the 6 vs 7-digit DATASUS/IBGE rule
2. SINASC live births by municipality of residence and year (denominator for children < 1 and 1 year)
3. PNI targets per vaccine and which dose completes each schedule, from the Ministry's technical notes → `seeds/pni_targets.csv` with source citation
4. Vaccine/dose code mapping table

## Acceptance criteria

- [ ] Each reference source documented in `sources.md` with URL and vintage
- [ ] `pni_targets.csv` cites the official document for every value

## Deliverables

- `docs/data/sources.md (reference section)`
- `seeds/pni_targets.csv`
- `seeds/vaccine_dose_map.csv`

## Why this matters (best practice)

Indicators are only as good as their denominators and thresholds. Versioning small reference tables with citations ("seeds") makes every target auditable — essential for accountability reporting.

## Notes

_Add decisions, problems found and links to the PR here while working._
