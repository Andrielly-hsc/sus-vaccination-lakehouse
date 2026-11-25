# Data sources

> **Status:** SI-PNI source verified on 2026-11-25 ([F02-T01](../tasks/F02-T01-source-discovery.md)).
> Reference data (IBGE, SINASC, PNI targets) is documented in [F02-T03](../tasks/F02-T03-reference-data-sources.md).
> All numbers below were measured with the scripts in [`scripts/discovery/`](../../scripts/discovery/)
> (see [§1.9](#19-how-to-reproduce)); none were copied from secondary sources.

## 1. SI-PNI — vaccine doses applied (facts)

### 1.1 Where it is published

| Item | Value |
|---|---|
| Portal | Portal de Dados Abertos do SUS — <https://dadosabertos.saude.gov.br> (the old `opendatasus.saude.gov.br` redirects here; the old CKAN API `/api/3/action/...` no longer answers) |
| Datasets | One per year: *Doses aplicadas pelo Programa de Nacional de Imunizações (PNI) - YYYY*, 2020 → 2026, e.g. <https://dadosabertos.saude.gov.br/dataset/doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2025> |
| Publisher | Departamento do Programa Nacional de Imunizações (DPNI), Ministry of Health; origin: Rede Nacional de Dados em Saúde (RNDS) |
| Resources per year | Monthly ZIPs in **CSV**, **JSON** and **XML**; a REST **API** (`apidadosabertos.saude.gov.br`); a **PDF data dictionary** |
| File URL pattern | `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/PNI/csv/vacinacao_{mmm}_{yyyy}_csv.zip`, with Portuguese month abbreviations `jan fev mar abr mai jun jul ago set out nov dez` |
| Data dictionary | <https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbbni/Dicionario_tb_ria_rotina.pdf> (60 fields; differs from the CSV, see §1.4) |
| Licence | **Not stated** (`license_id` empty, `isopen: false` in the portal metadata). Treated as public information under the Access to Information Law (Lei 12.527/2011): we cite the source, keep the raw data out of the repository and publish only aggregated, suppressed outputs. |

We use the **CSV** distribution: it is the smallest (Jan/2025: CSV 1.8 GB vs JSON 2.4 GB zipped)
and Spark reads it natively with an explicit schema.

### 1.2 File format (measured)

| Property | Value | Consequence for the pipeline |
|---|---|---|
| Container | ZIP with **one member** (`vacinacao_{mmm}_{yyyy}.csv`), DEFLATE | Stream-decompress; never extract to disk in full |
| Encoding | **ISO-8859-1 (Latin-1)**, not UTF-8 (first invalid UTF-8 byte at position 1 355) | Read with `encoding="ISO-8859-1"`; store UTF-8 from bronze on |
| Delimiter / quoting | `;`, header not quoted, no ragged rows in the sample | `sep=";"` |
| Line ending | CRLF, no BOM | Strip `\r` (Spark's CSV reader handles it) |
| Header | 56 columns, **identical** in Jan/2024, Jan/2025, Jun/2025, Dec/2025 and Jan/2026 | One source contract (v1) covers the whole scope |
| Dates | `YYYY-MM-DD` for `dt_vacina` and `dt_entrada_rnds` (**date only**, although the dictionary says TIMESTAMP) | Lag is measured in whole days |
| Row size | ≈ 590 bytes per row | Used for the estimates in §1.6 |

### 1.3 Sizes (HTTP `HEAD` + ZIP directory, 2026-11-25)

| Month | ZIP (compressed) | CSV (uncompressed) | Est. rows (÷ 590 B) | S3 `Last-Modified` |
|---|---:|---:|---:|---|
| Jan/2024 | 1.86 GB | 7.30 GB | ≈ 12.4 M | 2026-08-14 |
| Jan/2025 | 1.82 GB | 7.12 GB | ≈ 12.1 M | 2026-08-15 |
| Jun/2025 | 3.10 GB | 12.29 GB | ≈ 20.8 M | 2026-08-15 |
| Dec/2025 | 1.46 GB | 5.81 GB | ≈ 9.8 M | 2026-08-15 |
| Jan/2026 | 1.88 GB | 7.41 GB | ≈ 12.6 M | 2026-11-23 |

June is larger because of the influenza campaign. Row counts are **estimates**; exact counts are
recorded by the downloader's manifest (F03-T01).

### 1.4 Columns: CSV vs. the official dictionary

The CSV has 56 columns; the PDF dictionary lists 60. Eight CSV columns have a different name
from the dictionary, and four dictionary fields are not in the CSV:

| PDF dictionary | CSV (what we read) |
|---|---|
| `sg_vacina` | `sg_imunobiologico` |
| `ds_vacina` | `ds_nome` |
| `ds_dose_vacina` | `ds_tipo_dose` |
| `ds_estrategia_vacinacao` | `no_estrategia` |
| `ds_vacina_grupo_atendimento` | `no_grupo_atendimento` |
| `co_vacina_categoria_atendimento` | `co_categoria` |
| `ds_vacina_categoria_atendimento` | `ds_categoria` |
| `dt_deleted` | `dt_deletado_rnds` |
| `st_vida_paciente`, `dt_entrada_datalake`, `co_identificador_sistema`, `ds_identificador_sistema` | *(absent)* |

Other dictionary issues: field 11 is described as "UF name" but is `nu_cep_paciente` (in the data:
a **5-digit CEP prefix**); the facility name column keeps the typo `no_fantasia_estalecimento`.
**The data contract follows the CSV, not the PDF.** The full column-by-column dictionary is
[F02-T02](../tasks/F02-T02-data-dictionary.md).

### 1.5 Columns that drive the design

| Column | Meaning | Observed (50 000-row sample, Jan/2025) | Design decision |
|---|---|---|---|
| `co_documento` | ID of the FHIR document in the RNDS | UUID, unique in the sample | **Business key** `dose_id` (silver MERGE key) |
| `co_troca_documento`, `st_documento`, `dt_deletado_rnds` | Document that this one **replaces**; status (replaced/altered/final); deletion date | 1.0 % of rows replace another document; `st_documento` = `final` and `dt_deletado_rnds` empty in the sample | The source has **update/delete semantics**: silver must retire replaced documents, not only deduplicate (F05-T03) |
| `dt_vacina` | Vaccination date | 31 distinct days, all in January | **Event time** |
| `dt_entrada_rnds` | Date the record reached the RNDS | from the vaccination day to +583 days | **Processing time** → registration lag (timeliness indicator, replayer delays) |
| `co_paciente` | Pseudonymous patient ID (hash) | 49 824 distinct in 49 999 rows | Quasi-identifier; needed only for dropout logic — never leaves silver (F02-T06) |
| `nu_idade_paciente` | Age in **whole years** (no birth date in the CSV) | 29.5 % are `0` (under one year) | Age group for coverage; no birth-date minimisation needed |
| `co_municipio_paciente` / `co_municipio_estabelecimento` | Residence / facility municipality | **6 digits** (DATASUS form); 1.6 % of residence codes empty | Join on 6 digits; add the IBGE 7-digit code from reference data |
| `sg_uf_estabelecimento` | Facility UF | never empty | Downloader scope filter |
| `nu_cep_paciente` | First 5 digits of the residence CEP | 7.5 % empty | Quasi-identifier, not needed → **dropped in silver** |
| `co_vacina`, `sg_imunobiologico`, `co_dose_vacina`, `ds_tipo_dose` | Vaccine and dose | 65 vaccines, 39 dose codes (`1ª Dose`, `Única`, `Reforço`…) | Conformed through `seeds/vaccines.csv`, `seeds/doses.csv` and `seeds/coverage_indicators.csv` (F02-T03) |
| `no_estrategia` | Strategy (Rotina, Campanha, Especial…) | 79 % routine | Coverage indicators use routine doses (methodology, F06-T03) |

### 1.6 Registration lag — the data really arrives late

Lag = `dt_entrada_rnds − dt_vacina`, in days, on the 50 000-row sample:

| Statistic | Value |
|---|---|
| Median | **31 days** |
| 90th percentile | 58 days |
| 99th percentile | 363 days |
| Maximum | 583 days |
| Registered the same day | 22.4 % |
| Within 7 days | 31.6 % |
| Within 30 days | 49.0 % |
| Within 60 days | 90.4 % |
| Registered *before* vaccination | 0 |

The sample is the **first** 50 000 rows of the file, so it may be biased by the file's internal
order (its `dt_entrada_rnds` is concentrated in Feb/2025). The full distribution is measured on
the complete scope in F03 and reported per municipality in F06-T05.

Implications:

- "Real time" for this source means **provisional**: on any given day only about a quarter of that
  day's doses are already in the national system. The dashboard must say so (F11-T03).
- The replayer (F04-T02) derives each event's delay from this real lag distribution.
- The streaming watermark (F05-T04) cannot wait 583 days: events beyond it go to
  `silver.late_arrivals` and the batch path reconciles them.

### 1.7 Revisions and publication cadence

- Every 2025 monthly file was **re-published** in August 2026 (S3 `Last-Modified`), and the
  portal metadata was modified again on 2026-11-03; Jan/2026 was rewritten on 2026-11-23.
- Combined with lags of up to 583 days, this means **past months keep changing**. Months are
  not immutable snapshots.

Design consequences (F03):

- The downloader records `ETag` and `Last-Modified` per file in the manifest and re-downloads a
  month only when they change (cheap `HEAD` request).
- Bronze keeps each published version (append + `_source_file` / `_file_hash`); silver MERGEs on
  `dose_id`, so a re-published month updates rows instead of duplicating them.
- A configurable *revision window* (e.g. the last 18 months) is re-checked on every run.

### 1.8 Volume estimates for this project

| Scope | Rows | Landing (filtered, gzip) | Note |
|---|---|---|---|
| National, one month | ≈ 10–21 M | — | Never stored: filtered while streaming |
| Southeast (SP, MG, RJ, ES), one month | ≈ 38 % → 4–8 M | ≈ 0.7 GB | `base` profile |
| Southeast, 24 months | ≈ 110 M | ≈ 17 GB | Plus bronze/silver Delta tables of similar order |
| `dev` profile: ES + SP, 3 months | ≈ 22.5 % → ≈ 8 M | ≈ 1.2 GB | Day-to-day development |

These volumes do not fit the 12 GB currently free on drive C:, where WSL stores its virtual disk.
The WSL distribution should be moved to drive D: before F03 (see [setup.md](../setup.md)).

### 1.9 How to reproduce

The scripts read only the ZIP directory and the first megabytes through HTTP `Range` requests
(≈ 8 MB for 50 000 rows instead of 1.8 GB). Samples contain anonymised personal data: write them
**outside** the repository.

```bash
python -I scripts/discovery/remote_zip_sample.py \
  https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/PNI/csv/vacinacao_jan_2025_csv.zip \
  ~/vaxlake-data/discovery/jan_2025 --lines 50000
python -I scripts/discovery/profile_sample.py ~/vaxlake-data/discovery/jan_2025/sample_head.csv
```

## 2. Reference data

> Verified on 2026-11-25 ([F02-T03](../tasks/F02-T03-reference-data-sources.md)).

### 2.1 IBGE municipalities

| Item | Value |
|---|---|
| Source | IBGE *API de Localidades* — <https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado> (JSON, no key) |
| Content | 5 571 municipalities: 7-digit IBGE code, name, UF, region, plus micro/meso and immediate/intermediate regions |
| Code rule | The DATASUS/SI-PNI 6-digit code is the IBGE code **without its last (check) digit**; the first 6 digits are unique across all 5 571 municipalities |
| Check against SI-PNI (300 000 rows) | Every facility municipality code matches. Residence codes not found: `999999` (unknown residence, 31 rows) and one invalid code → treated as missing |
| Vintage | Current list at download time; the vintage (download date) is stored with the table because municipalities are occasionally created |
| Southeast | 1 668 municipalities (SP 645, MG 853, RJ 92, ES 78) |

### 2.2 SINASC — live births (coverage denominator)

| Item | Value |
|---|---|
| Dataset | *Sistema de Informação sobre Nascidos Vivos – Sinasc* — <https://dadosabertos.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc> |
| Licence | Creative Commons Attribution (portal metadata) |
| Files | One ZIP per year in CSV/JSON/XML: `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINASC/csv/SINASC_{yyyy}_csv.zip` (from 2016; older years use `DNBR{yyyy}`). 2024 is final; **2025 is preliminary and 2026 a "2nd preview"** |
| Format (2024, measured) | 92 MB ZIP → 562 MB CSV, `;`, valid UTF-8, 62 columns, **one row per birth** |
| Columns we use | `CODMUNRES` (residence municipality, 6 digits), `DTNASC` (birth date, `DDMMYYYY`) |
| Minimisation | Each row describes a birth and the mother (age, schooling, race/colour, pregnancy history). We only need **counts of births per residence municipality and year**, so the ingestion aggregates while reading and never stores the microdata (F02-T06) |
| Rule (NT 90/2025) | SINASC is the denominator for children under 1 and 1 year old; while the current year is not consolidated, the **previous year** is used |

### 2.3 Vaccine, dose and coverage-indicator reference tables

Curated seeds in [`seeds/`](../../seeds/README.md): `vaccines.csv` (80 codes), `doses.csv`
(49 codes) and `coverage_indicators.csv` (15 childhood indicators with vaccines, doses required,
target age, minimum interval and target). Each value cites its source in `seeds/README.md`.

### 2.4 Coverage methodology (official)

**Nota Técnica nº 90/2025-DPNI/SVSA/MS** (17/12/2025, revokes NT 117/2024) defines the method in
force since 2024:

- Coverage = people who completed the schedule ÷ eligible population × 100.
- The numerator counts **individuals (CNS/CPF), not doses**, in two stages: (1) people with enough
  doses for the schedule, respecting minimum/maximum age and minimum interval, *whatever the
  "dose type" field says*; (2) people not included in stage 1 but whose last dose is recorded with
  the completing "dose type". The share of stage-2 people is itself a **data-quality indicator**.
- Each individual is counted once; the only numerator source is the RNDS.
- The old method (1994–2023) counted the last dose by "dose type", which explains historical
  coverages above 100 %.

Consequences for this project: silver keeps `patient_key` (the RNDS pseudonymous patient hash)
so gold can follow patients across months and reproduce both stages; with age only in whole
years, age limits in months are approximated (F06-T03).

Calendar rules (doses, ages, intervals) come from the **Instrução Normativa do Calendário
Nacional de Vacinação 2025**; targets (90 % BCG and rotavirus, 95 % the others) from the CNM
technical study (2026), a secondary source citing the national calendar — see the caveats in
[`seeds/README.md`](../../seeds/README.md).

## 3. Data-quality caveats found so far

- Encoding is Latin-1 and the dictionary does not match the file (§1.4).
- `dt_entrada_rnds` is a date, not a timestamp, despite the dictionary.
- 1.6 % of rows have no residence municipality; 10.9 % have no facility type and no
  administration route/site.
- 1 % of documents replace an earlier document (`co_troca_documento`).
- A 2021 technical note by Transparência Brasil reported duplicates and the absence of a unique
  patient key in the COVID-19 vaccination open data
  (<https://www.transparencia.org.br/downloads/publicacoes/Nota_Tecnica_Vacinacao_04032021.pdf>);
  to be checked on the routine data in F05.
- Coverage computed from doses and SINASC can exceed 100 % (denominator issues, vaccination
  outside the municipality of residence).
