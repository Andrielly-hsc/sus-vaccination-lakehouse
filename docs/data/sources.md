# Data sources

> **Status:** initial notes from planning (2026-11-25). To be completed and verified in
> [F02-T01](../tasks/F02-T01-source-discovery.md) and [F02-T03](../tasks/F02-T03-reference-data-sources.md).
> Nothing here is confirmed until it has been checked against a downloaded file.

## 1. SI-PNI — vaccine doses applied (facts)

| Item | What we know so far | To verify |
|---|---|---|
| Publisher | Ministry of Health — OpenDataSUS portal | Dataset page URL and licence |
| Content | Individual, anonymised vaccination records (one row per dose), CSV and API | Exact resource names per month |
| Coverage | 2020 onwards as individual records; older years only as aggregates (DATASUS FTP, `.DBF`) | Last month available |
| Size | ~1.4 GB per national monthly CSV | Size per month for the Southeast scope |
| Columns | ~47 in the CSV (the JSON mirror has different names) | Full header, encoding, delimiter |
| Event time | Vaccination date | Column name, format |
| Processing time | Date the record reached the national network (RNDS import) | Column name, format |
| Revisions | Unknown | Are past months republished? |

Planning references:

- Ministry of Health — vaccination open data (active transparency): <https://www.gov.br/saude/pt-br/acesso-a-informacao/sic/dados-em-transparencia-ativa/svsa/vacinacao>
- healthbR R package, SI-PNI vignette (describes the OpenDataSUS monthly files): <https://cloud.r-project.org/web/packages/healthbR/vignettes/sipni-vaccination.html>
- Ministry of Health — technical guide on nominal vaccination data: <https://www.gov.br/saude/pt-br/vacinacao/publicacoes/instrutivo-tecnico-coleta-e-analise-nominal-de-dados-vacinais>

## 2. Reference data

| Source | Use | To verify |
|---|---|---|
| IBGE municipalities | Municipality names, UF, region; 7-digit code (DATASUS uses 6) | Download URL, vintage |
| SINASC live births | Coverage denominator for children < 1 and 1 year | Open data location, latest final year |
| PNI technical notes | Coverage targets per vaccine; dose that completes each schedule | Official document per value |

## 3. Known data-quality caveats (from the literature, to confirm)

- Duplicate records and no unique patient identifier across systems have been reported for OpenDataSUS vaccination data.
- Column names differ between the CSV and JSON distributions.
- Coverage computed from doses and SINASC can exceed 100 % (denominator issues, vaccination outside the municipality of residence).
