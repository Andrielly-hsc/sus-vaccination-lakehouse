# Privacy assessment (LGPD / GDPR)

> **Status:** v1, 2026-11-25 ([F02-T06](../tasks/F02-T06-privacy-assessment.md)).
> This is a **technical** assessment written by the data engineer to design the pipeline, not
> legal advice. It follows the structure of a data-protection impact assessment (description,
> necessity, risks, measures) at the scale of a portfolio project.

## 1. What is processed and why

| Item | Description |
|---|---|
| Purpose | Compute and publish **aggregated** public-health accountability indicators per municipality (coverage vs target, dropout, homogeneity, registration timeliness) and demonstrate lakehouse engineering. |
| Data | SI-PNI doses applied (OpenDataSUS), published **anonymised** by the Ministry of Health; SINASC live births; IBGE municipalities ([sources.md](sources.md)). |
| Subjects | Every person vaccinated in the scope (Southeast Brazil, 2024–2025): mostly **children**. |
| Environment | One developer's laptop (WSL2) and GitHub Actions with synthetic fixtures. No server, no other users, no copy in the cloud. |
| Outputs | Gold aggregates, the dashboard and the README. No record-level data is ever published. |

## 2. Legal context

| Topic | Brazil — LGPD (Lei 13.709/2018) | EU — GDPR (for comparison) |
|---|---|---|
| Health data, racial/ethnic origin | **Sensitive personal data** (art. 5, II; processing rules in art. 11) | Special categories (art. 9) |
| Anonymised data | Not personal data, **unless** the anonymisation can be reversed with reasonable efforts (art. 12) | Recital 26 |
| Pseudonymised data (e.g. a stable hash per person) | Still personal data; recommended for public-health studies (art. 13) | Personal data (art. 4(5), recital 26) |
| Publicly accessible data | Processing must respect the purpose, good faith and public interest that justified its publication (art. 7, §3) | Purpose limitation (art. 5(1)(b)) |
| Principles | Purpose, necessity (minimisation), security, prevention (art. 6) | Art. 5 (minimisation, integrity, storage limitation) |
| Access to public information | Lei 12.527/2011 (LAI) underpins the publication of the open data | — |

Consequence: the source is called anonymised, but it contains a **stable pseudonymous patient
code** (`co_paciente`) and several quasi-identifiers. We therefore treat the record-level data as
**pseudonymous personal data, including sensitive data**, and apply minimisation, security and
disclosure control — the cautious reading of art. 12.

## 3. What could identify a person

### 3.1 Identifiers and quasi-identifiers in the source

| Kind | Columns | Note |
|---|---|---|
| Pseudonym | `co_paciente` | Stable across months: links all doses of one person |
| Location | `co_municipio_paciente`, `nu_cep_paciente` (5-digit CEP prefix), `sg_uf_paciente` | The CEP prefix narrows a big city to a few neighbourhoods |
| Demographics | `nu_idade_paciente` (whole years), `tp_sexo_paciente` | No birth date in the file |
| Event | `dt_vacina`, `co_vacina`, `co_cnes_estabelecimento` | A visit to a clinic on a given day is observable by neighbours |
| Sensitive | race/colour, indigenous ethnicity, pregnancy status, priority groups (incl. comorbidities, people deprived of liberty) | Special categories |

### 3.2 Measured risk (k-anonymity on 300 000 sample rows)

Share of records that are **unique**, or in an equivalence class smaller than *k* = 5, for each
combination of quasi-identifiers ([`scripts/discovery/reidentification_risk.py`](../../scripts/discovery/reidentification_risk.py)):

| Quasi-identifiers | Records unique | Records in classes < 5 |
|---|---:|---:|
| municipality | 0.0 % | 0.8 % |
| municipality + sex | 0.3 % | 3.0 % |
| municipality + age | 16.8 % | 35.6 % |
| municipality + age + sex | 23.2 % | 45.3 % |
| municipality + month + vaccine | 14.0 % | 33.7 % |
| municipality + date + age + sex | **68.9 %** | 89.5 % |
| municipality + date + age + sex + race | **78.2 %** | 93.8 % |
| CEP prefix + date + age + sex | **89.1 %** | 96.7 % |

For infants (age 0), 90.6 % of the cells *municipality × month × vaccine* hold fewer than 5
records in the sample.

**How to read it.** The sample is a small fraction of a month, so classes are smaller than in
the full data: the numbers are an **upper bound** and serve to *compare* combinations. The
conclusion is robust anyway: record-level rows with date, age, sex and place are close to unique
and must stay inside the lakehouse, while counts per municipality are safe only when they are
not small.

### 3.3 Risk scenarios

| # | Scenario | Likelihood | Impact | Main measure |
|---|---|---|---|---|
| R1 | Someone who knows a child's town, age, sex and vaccination day finds the child's record and the rest of its history via `co_paciente` | Medium (record-level data) | High (health data of a child) | Record-level data never leaves the lakehouse (P3, P4) |
| R2 | A published coverage of a tiny municipality reveals that one specific child is unvaccinated (e.g. 7 of 8 births vaccinated) | Medium | High | Small-cell suppression on counts **and complements** (P6) |
| R3 | Sensitive attributes (race, pregnancy, comorbidities) are joined to vaccination records | Low after minimisation | High | Dropped in silver (P1, P2) |
| R4 | Raw files leak through git or a public artefact | Low | High | Data git-ignored, large-file hook, samples outside the repo (P4) |
| R5 | Real-time panel shows a single dose in a small town in the last hour | Medium | Medium | Same suppression on the real-time view (P6, P10) |

## 4. Measures (rules the pipeline enforces)

| ID | Rule | Implemented in |
|---|---|---|
| **P1** | **Minimisation**: silver keeps 35 of 56 columns; the CEP prefix, nationality, body site/route, names duplicated from reference data and all sensitive columns are dropped | [data dictionary](data_dictionary.md), silver contract (F02-T04), F05-T01 |
| **P2** | Sensitive columns (race/colour, ethnicity, pregnancy, priority groups/categories) never leave **bronze**; a test asserts they are absent from silver | F05-T01, F05-T06 |
| **P3** | `patient_key` (pseudonym) exists only in silver, where the official individual-based coverage method needs it; **no gold table, export, log line or dashboard contains it** | silver/gold contracts, F06-T01, test in F06 |
| **P4** | No record-level data in git: `data/` ignored, large-file hook, discovery samples kept outside the repository; CI uses fictitious fixtures only | F01 (done), F03-T06 fixtures |
| **P5** | SINASC microdata (births and mothers) is **aggregated while reading**; only counts per municipality and year are stored | bronze contract, F03-T05 |
| **P6** | **Small-cell suppression** in everything published: a count below *k* = 5 (`privacy.suppression_threshold`) is hidden, and so is a coverage whose numerator **or complement** (target population − vaccinated) is below *k*; flagged `is_suppressed`, shown as "suppressed", never as 0 | gold indicators (F06-T03/T04/T05), dashboard (F11-T03) |
| **P7** | Published geography stops at the **municipality**; facility-level outputs are only timeliness statistics over ≥ *k* doses | F06-T05 |
| **P8** | **No linkage** with other datasets to single out people; purpose limited to aggregated indicators | data card (F09-T05) |
| **P9** | **Storage limitation**: bronze keeps 3 years; `VACUUM` removes old file versions; local data can be deleted and rebuilt from the public source | contracts SLA, F09-T04 |
| **P10** | Quarantine and late-arrival tables hold raw payloads: same restrictions as bronze, never exported; the real-time panel applies P6 | silver contracts, F11 |
| **P11** | Access: single-user local environment. In a shared deployment, bronze/silver would be restricted to engineers (table ACLs, e.g. Unity Catalog or Fabric roles) and analysts would read gold only | ARCHITECTURE §6.8, F09 |

## 5. What may be published

| Output | Allowed content |
|---|---|
| README, report, screenshots | Aggregates by municipality/UF/region and year or month, after P6 |
| Dashboard | Gold tables only; suppressed cells marked; real-time counts by municipality and hour after P6 |
| Repository | Code, contracts, seeds, documentation, synthetic fixtures — **never** downloaded data or samples |
| CI artefacts | Test reports on fixtures only |

## 6. Residual risk and review

With P1–P11 the published outputs contain no record-level data and no small cells, so the
residual risk is low. The main residual risk is the **local** record-level copy (bronze/silver),
mitigated by keeping it on one machine, out of git, with limited retention.

Review this assessment when: a new column is kept in silver, a new output is published, the
suppression threshold changes, or the project moves to a shared environment.
