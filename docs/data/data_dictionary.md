# Data dictionary — SI-PNI doses applied

> **Status:** v1, 2026-11-25 ([F02-T02](../tasks/F02-T02-data-dictionary.md)).
> Source format and provenance: [sources.md](sources.md). Privacy rules behind the keep/drop
> decisions are detailed in the privacy assessment ([F02-T06](../tasks/F02-T06-privacy-assessment.md)).
> Observed values come from 300 000 sample rows (Jan/2025 and Jun/2025) produced with
> [`scripts/discovery/code_values.py`](../../scripts/discovery/code_values.py).

## 1. How to read this dictionary

| Layer | Column names | Types | Columns |
|---|---|---|---|
| **Bronze** | Source names, unchanged (`co_documento`, `dt_vacina`, …) | all `string` | all 56 + ingestion metadata |
| **Silver** | English `snake_case` names (this table) | typed | 35 kept + derived columns (§3) |

**Naming rules** (ARCHITECTURE §6.2): English, `snake_case`; `_code` for codes, `_name` for
descriptions, `_date` for dates, `_at` for timestamps, `is_` for booleans. Codes are kept as
**strings** even when numeric, because leading zeros matter (`03` ≠ `3`) and nobody does
arithmetic on them.

**Classification** (drives privacy handling):

| Class | Meaning | Rule |
|---|---|---|
| `id` | Technical identifier of a record | Keep |
| `pseudonym` | Stable code for a person (hash) | Silver only, never in gold or outputs |
| `quasi` | Quasi-identifier: identifies a person when combined (place, age, sex) | Keep only if an indicator needs it; aggregate and suppress small counts in gold |
| `sensitive` | Sensitive personal data under LGPD art. 5 II (racial/ethnic origin, health) beyond the vaccination itself | Drop unless an indicator needs it |
| `org` | About an organisation (facility, manufacturer), not a person | Keep |
| `operational` | About the record, the vaccine or the process | Keep if useful |

## 2. Column mapping (56 source columns)

| # | Source column | Silver column | Type | Null in sample | Class | Keep | Notes |
|---:|---|---|---|---:|---|---|---|
| 1 | `co_documento` | `dose_id` | string | 0 % | id | ✅ | UUID of the RNDS document. **Primary key**; unique in all samples |
| 2 | `co_paciente` | `patient_key` | string | 0 % | pseudonym | ✅ silver only | Hash assigned by the RNDS. **Required by the official coverage method since 2024**, which counts vaccinated *individuals* with a complete schedule (NT 90/2025-DPNI, see sources.md §2.4); also used to detect duplicate doses. Never propagated to gold |
| 3 | `tp_sexo_paciente` | `sex` | string | 0 % | quasi | ✅ | `F`, `M`, `I` (indeterminate, 13 rows) |
| 4 | `co_raca_cor_paciente` | — | — | 0 % | sensitive | ❌ | Racial origin; not used by any indicator (minimisation). Equity analysis would need a new privacy review |
| 5 | `no_raca_cor_paciente` | — | — | 0 % | sensitive | ❌ | Description of #4 |
| 6 | `co_municipio_paciente` | `residence_municipality_code` | string(6) | 1.5 % | quasi | ✅ | **6-digit** DATASUS code. Coverage is counted by residence. 7-digit IBGE code added in silver (§3) |
| 7 | `co_pais_paciente` | `residence_country_code` | string | 1.5 % | quasi | ✅ | `10` = Brazil; foreign residents are excluded from municipal coverage |
| 8 | `no_municipio_paciente` | — | — | 1.5 % | quasi | ❌ | Name comes from the IBGE reference table instead |
| 9 | `no_pais_paciente` | — | — | 1.5 % | quasi | ❌ | Redundant with #7 |
| 10 | `sg_uf_paciente` | `residence_uf` | string(2) | 1.5 % | quasi | ✅ | Redundant with #6 but cheap and useful for validation |
| 11 | `nu_cep_paciente` | — | — | 7.3 % | quasi | ❌ | **5-digit CEP prefix** (the PDF calls it "UF name"). Fine-grained location, not needed |
| 12 | `ds_nacionalidade_paciente` | — | — | 0 % | quasi | ❌ | `B` Brazilian, `E` foreign, `N` naturalised; not needed |
| 13 | `no_etnia_indigena_paciente` | — | — | 99.6 % | sensitive | ❌ | Ethnic origin |
| 14 | `co_etnia_indigena_paciente` | — | — | 99.6 % | sensitive | ❌ | Ethnic origin |
| 15 | `co_cnes_estabelecimento` | `establishment_code` | string(7) | 0 % | org | ✅ | CNES. 3 rows in 300 000 have **14 characters** and no facility municipality → validity rule (quarantine) |
| 16 | `no_razao_social_estabelecimento` | `establishment_legal_name` | string | 0 % | org | ✅ | Attribute of the establishment dimension (SCD2) |
| 17 | `no_fantasia_estalecimento` | `establishment_name` | string | 0 % | org | ✅ | Source keeps the typo *estalecimento* |
| 18 | `co_municipio_estabelecimento` | `facility_municipality_code` | string(6) | 0 % | org | ✅ | Where the dose was applied (timeliness by facility) |
| 19 | `no_municipio_estabelecimento` | — | — | 0 % | org | ❌ | From the IBGE reference table |
| 20 | `sg_uf_estabelecimento` | `facility_uf` | string(2) | 0 % | org | ✅ | Downloader scope filter |
| 21 | `co_troca_documento` | `replaces_dose_id` | string | 98.8 % | id | ✅ | Document this one **replaces**: the replaced `dose_id` must be retired in silver. None of the 3 585 referenced documents was in the same sample → replacements usually point to earlier files |
| 22 | `co_vacina` | `vaccine_code` | string | 0 % | operational | ✅ | 80 codes observed (§4.6) |
| 23 | `sg_imunobiologico` | `vaccine_acronym` | string | 0 % | operational | ✅ | `BCG`, `Penta`, `VIP`, `SCR`… (PDF name: `sg_vacina`) |
| 24 | `dt_vacina` | `vaccination_date` | date | 0 % | operational | ✅ | **Event time.** `YYYY-MM-DD` |
| 25 | `co_dose_vacina` | `dose_code` | string | 0 % | operational | ✅ | 49 codes (§4.2) |
| 26 | `ds_tipo_dose` | `dose_name` | string | 0 % | operational | ✅ | PDF name: `ds_dose_vacina` |
| 27 | `co_local_aplicacao` | — | — | 8.4 % | operational | ❌ | Body site; clinical detail not needed |
| 28 | `ds_local_aplicacao` | — | — | 8.4 % | operational | ❌ | |
| 29 | `co_via_administracao` | — | — | 8.4 % | operational | ❌ | Route of administration; not needed |
| 30 | `ds_via_administracao` | — | — | 8.4 % | operational | ❌ | |
| 31 | `co_lote_vacina` | `vaccine_lot` | string | 1.0 % | operational | ✅ | Free text; useful for operational analysis |
| 32 | `ds_vacina_fabricante` | `manufacturer_name` | string | 2.7 % | org | ✅ | Free text |
| 33 | `dt_entrada_rnds` | `registered_date` | date | 0 % | operational | ✅ | **Processing time** (date only, although the PDF says TIMESTAMP) |
| 34 | `co_sistema_origem` | `source_system_code` | string | 0 % | operational | ✅ | One code **per installation** (4 528 codes in the sample), not per product |
| 35 | `ds_sistema_origem` | `source_system_name` | string | 0 % | operational | ✅ | Free text (e.g. *ESUS APS - NACIONAL (OFFLINE)*, *Novo PNI*); one code had two names. Explains part of the registration lag |
| 36 | `st_documento` | `document_status` | string | 0 % | operational | ✅ | Only `final` observed; the PDF says it marks replaced/altered documents |
| 37 | `co_estrategia_vacinacao` | `strategy_code` | string | 0.8 % | operational | ✅ | `1` Rotina = 75 % (§4.3). Code `0` appears without a name (522 rows) |
| 38 | `no_estrategia` | `strategy_name` | string | 1.0 % | operational | ✅ | PDF name: `ds_estrategia_vacinacao` |
| 39 | `co_origem_registro` | `record_origin_code` | string | 94 % | operational | ✅ | `01` transcription from the vaccination card, `02` vaccinated abroad, `99` without description |
| 40 | `ds_origem_registro` | `record_origin_name` | string | 96 % | operational | ✅ | Transcribed doses are old doses registered now → excluded from timeliness |
| 41 | `co_vacina_grupo_atendimento` | — | — | 61.6 % | sensitive | ❌ | Priority group (COVID-era); can reveal health/occupation |
| 42 | `no_grupo_atendimento` | — | — | 62.9 % | sensitive | ❌ | |
| 43 | `co_categoria` | — | — | 63 % | sensitive | ❌ | Includes *Comorbidades*, *Pessoas com Deficiência*, *População Privada de Liberdade* |
| 44 | `ds_categoria` | — | — | 63 % | sensitive | ❌ | |
| 45 | `co_vacina_fabricante` | `manufacturer_code` | string | 49.4 % | org | ✅ | |
| 46 | `ds_nome` | `vaccine_name` | string | 0 % | operational | ✅ | Full name (PDF name: `ds_vacina`) |
| 47 | `ds_condicao_maternal` | — | — | 74 % | sensitive | ❌ | Pregnancy status (health data). Needed only for maternal-vaccination indicators, out of scope |
| 48 | `co_tipo_estabelecimento` | `establishment_type_code` | string | 8.4 % | org | ✅ | 30 CNES types (§4.4) |
| 49 | `ds_tipo_estabelecimento` | `establishment_type_name` | string | 8.4 % | org | ✅ | |
| 50 | `co_natureza_estabelecimento` | `establishment_nature_code` | string | 8.4 % | org | ✅ | Public / private / non-profit / individual (§4.5) |
| 51 | `ds_natureza_estabelecimento` | `establishment_nature_name` | string | 8.4 % | org | ✅ | |
| 52 | `nu_idade_paciente` | `age_years` | int | 0 % | quasi | ✅ | Whole years, 0–116 observed; `0` = under one year. No birth date exists in the file |
| 53 | `co_condicao_maternal` | — | — | 74 % | sensitive | ❌ | Code of #47 |
| 54 | `no_uf_paciente` | — | — | 1.5 % | quasi | ❌ | Redundant with #10 |
| 55 | `no_uf_estabelecimento` | — | — | 0 % | org | ❌ | Redundant with #20 |
| 56 | `dt_deletado_rnds` | `deleted_at` | timestamp | 100 % | operational | ✅ | Deletion in the RNDS (PDF: `dt_deleted`). Always empty in the samples — format unknown; parsed leniently, rows with a value are treated as deleted |

**Summary:** 35 columns kept, 21 dropped: 10 sensitive (racial/ethnic origin, health condition,
priority group), 5 redundant with reference data or other columns, 6 not needed by any indicator.

## 3. Derived silver columns

| Column | Type | Rule | Why |
|---|---|---|---|
| `vaccination_month` | string `YYYY-MM` | from `vaccination_date` | Partition column of `silver.vaccination_doses` |
| `registration_lag_days` | int | `registered_date − vaccination_date` | Timeliness indicator; replayer delays |
| `residence_municipality_code_7` | string(7) | 6-digit code joined to the IBGE table | Conformance with IBGE-based reference data |
| `is_replacement` | boolean | `replaces_dose_id` not null | Update semantics (F05-T03) |
| `is_deleted` | boolean | `deleted_at` not null | Delete semantics |
| `is_transcription` | boolean | `record_origin_code` in (`01`, `02`) | Exclude old doses from timeliness |
| `age_group` | string | `<1`, `1`, `2-4`, … (bands defined with the coverage methodology, F06-T03) | Coverage target populations |

Plus the technical columns carried from bronze: `_ingested_at`, `_source_file`, `_file_hash`,
`_batch_id`.

## 4. Code systems (observed values)

Every code maps to exactly one description in the samples, except one `source_system_code`.

### 4.1 Sex — `sex`

| Code | Meaning | Rows |
|---|---|---:|
| `F` | Female | 159 744 |
| `M` | Male | 140 243 |
| `I` | Indeterminate | 13 |

### 4.2 Dose — `dose_code` → `dose_name` (top 15 of 49)

| Code | Name | Rows |
|---|---|---:|
| `9` | Única (single dose) | 95 586 |
| `1` | 1ª Dose | 61 721 |
| `2` | 2ª Dose | 46 360 |
| `38` | Reforço (booster) | 36 204 |
| `8` | Dose | 26 857 |
| `3` | 3ª Dose | 17 750 |
| `6` | 1º Reforço | 6 927 |
| `7` | 2º Reforço | 5 598 |
| `10` | Revacinação | 1 560 |
| `4` | 4ª Dose | 421 |
| `32` | 1ª Dose Revacinação | 195 |
| `57` | Dose Zero | 138 |
| `59` | Profilaxia/Tratamento com 1 unidade | 119 |
| `33` | 2ª Dose Revacinação | 79 |
| `36` | Dose Inicial | 56 |

The remaining 34 codes (≤ 56 rows each) are revaccinations, "doubled"/fractional doses and
serum/immunoglobulin treatments. Which dose **completes the schedule** of each vaccine is defined
in `seeds/coverage_indicators.csv`; all dose codes are classified in `seeds/doses.csv` (F02-T03).

### 4.3 Strategy — `strategy_code` → `strategy_name`

| Code | Name | Rows | | Code | Name | Rows |
|---|---|---:|---|---|---|---:|
| `1` | Rotina | 225 778 | | `6` | Campanha Seletiva | 302 |
| `2` | Especial | 30 481 | | `10` | Pesquisa | 229 |
| `5` | Campanha Indiscriminada | 26 578 | | `9` | Monitoramento das Estratégias de Vacinação | 212 |
| `8` | Serviço Privado | 9 237 | | `11` | Pré-exposição | 123 |
| *(empty)* | | 2 491 | | `7` | Soroterapia | 86 |
| `12` | Pós-exposição | 1 907 | | `3` | Bloqueio | 63 |
| `14` | Vacinação Escolar | 1 273 | | `13` | Reexposição | 34 |
| `4` | Intensificação | 657 | | `15` | Operação Gota | 27 |
| `0` | *(no name)* | 522 | | | | |

### 4.4 Establishment type — `establishment_type_code` (top 10 of 30)

| Code | Name | Rows |
|---|---|---:|
| `02` | Centro de Saúde/Unidade Básica | 231 588 |
| *(empty)* | | 25 223 |
| `01` | Posto de Saúde | 6 802 |
| `05` | Hospital Geral | 6 535 |
| `36` | Clínica/Centro de Especialidade | 6 463 |
| `85` | Centro de Imunização | 5 942 |
| `04` | Policlínica | 5 183 |
| `39` | Unidade de Apoio Diagnose e Terapia | 1 842 |
| `07` | Hospital Especializado | 1 580 |
| `72` | Unidade de Atenção à Saúde Indígena | 1 262 |

### 4.5 Establishment nature — `establishment_nature_code`

| Code | Name | Rows |
|---|---|---:|
| `1` | Administração Pública | 261 432 |
| *(empty)* | | 25 223 |
| `2` | Entidades Empresariais | 10 803 |
| `3` | Entidades sem Fins Lucrativos | 2 517 |
| `4` | Pessoas Físicas | 25 |

### 4.6 Vaccines — `vaccine_code` (childhood schedule and most frequent)

80 vaccine, serum and immunoglobulin codes were observed. The ones relevant to the childhood
coverage indicators (F06):

| Code | Acronym | Name (source) | Rows |
|---|---|---|---:|
| `15` | BCG | vacina BCG | 4 880 |
| `9` | HB | vacina hepatite B (recombinante) | 19 980 |
| `42` | Penta | difteria, tétano, pertussis, hepatite B e Haemophilus influenzae B | 13 926 |
| `22` | VIP | poliomielite 1, 2 e 3 (inativada) | 23 808 |
| `45` | ROTA | rotavírus humano G1P[8] (atenuada) | 8 770 |
| `26` | VPC10 | pneumocócica 10-valente (conjugada) | 13 091 |
| `41` | MenC | meningocócica C (conjugada) | 10 132 |
| `14` | VFA | febre amarela (atenuada) | 16 569 |
| `24` | SCR | sarampo, caxumba, rubéola (tríplice viral) | 10 014 |
| `56` | SCRV | sarampo, caxumba, rubéola e varicela (tetra viral) | 6 070 |
| `34` | VZ | varicela (atenuada) | 3 627 |
| `55` | HAinf | hepatite A (inativada, infantil) | 5 063 |
| `46` | DTP | difteria, tétano e pertussis | 9 512 |
| `43` | Hexa acelular | hexavalente acelular (special use, CRIE) | 849 |

Most frequent overall: `33` INF3 influenza trivalente (72 481, campaign month), `25` dT
(20 826), `74` MenACWY (10 884), `104` DNG dengue (9 646), `67` HPV4 (7 073), COVID-19 vaccines
(`112`, `102`, `87`, `97` …). The full list is generated by the script; the mapping used by the
pipeline are `seeds/vaccines.csv` and `seeds/coverage_indicators.csv` (F02-T03).

### 4.7 Record origin — `record_origin_code`

| Code | Name | Rows |
|---|---|---:|
| *(empty)* | Regular record | 281 998 |
| `01` | Registro anterior / Transcrição de caderneta | 10 910 |
| `99` | *(no name)* | 7 085 |
| `02` | Vacina no Exterior | 7 |

## 5. Validity rules derived from this dictionary

These become data-contract quality rules (F02-T04) and silver validations (F05-T02):

| Rule | Severity |
|---|---|
| `dose_id` not null and unique | critical |
| `vaccination_date` is a valid date, not in the future, ≥ 2020-01-01 | critical |
| `registered_date` ≥ `vaccination_date` | critical (0 violations in samples) |
| `establishment_code` has 7 digits | quarantine row |
| `facility_municipality_code` and `facility_uf` not null | quarantine row |
| `residence_municipality_code` has 6 digits when present | quarantine row |
| `age_years` between 0 and 130 | quarantine row |
| `sex` in (`F`, `M`, `I`) | quarantine row |
| `vaccine_code` and `dose_code` exist in `seeds/vaccines.csv` / `seeds/doses.csv` | warning (new codes appear over time) |
| `residence_municipality_code` not null in ≥ 97 % of rows | warning |
