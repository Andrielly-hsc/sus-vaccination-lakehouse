# Seeds — small, versioned reference tables

Seeds are reference data that change rarely and are curated by hand or by a documented
script. They are versioned in git (unlike `data/`), so every indicator can be traced to the
exact targets and code lists used. All files: UTF-8, comma-separated, header in the first line.

| File | Content | Built by | Source |
|---|---|---|---|
| `vaccines.csv` | Every vaccine, serum, immunoglobulin and monoclonal-antibody code observed in SI-PNI (80) with acronym, name and `product_type` | `scripts/discovery/build_code_seeds.py` | SI-PNI samples, Jan/2025 + Jun/2025 (300 000 rows) |
| `doses.csv` | Every dose code observed (49) with `dose_kind` (primary, single, booster, revaccination, zero, initial, additional, treatment, unspecified) and `dose_number` | same script | same samples |
| `coverage_indicators.csv` | One row per childhood coverage indicator: vaccines that count, doses required, completing dose codes, target age, minimum interval, denominator, **target %** | by hand, from the documents below | see below |

## Sources for `coverage_indicators.csv`

| Column(s) | Source |
|---|---|
| Method: individual-based numerator in two stages (enough doses respecting age and minimum interval; otherwise the last dose by "dose type"), SINASC denominator for children under 1 and 1 year old | Ministry of Health, **Nota Técnica nº 90/2025-DPNI/SVSA/MS** (17/12/2025), which revokes NT 117/2024 — <https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2025/nota-tecnica-no-90-2025-dpni-svsa-ms.pdf> |
| `vaccine_codes`, `doses_required`, ages, `min_interval_days` | Ministry of Health, **Instrução Normativa do Calendário Nacional de Vacinação 2025** — <https://www.gov.br/saude/pt-br/vacinacao/publicacoes/instrucao-normativa-que-instrui-o-calendario-nacional-de-vacinacao-2025.pdf> (e.g. VIP and MenACWY replacing VOPb and MenC in boosters; booster intervals of 60 days and 6 months) |
| `target_pct` (90 % BCG and rotavirus, 95 % the others) | **Confederação Nacional de Municípios (CNM)**, *Estudo Técnico — Avaliação das coberturas vacinais de rotina no Brasil* (2026), Quadro 1, which cites the Calendário Nacional de Vacinação 2024 — <https://cnm.org.br/storage/biblioteca/2026/Estudos_Tecnicos/ET_SAU_01-2026_Avaliacao_coberturas_Vacinais_rotina_Brasil.pdf>. The four "pact" indicators (penta D3, polio D3, pneumo10 D2, MMR D1) at 95 % are also in Portaria GM/MS nº 6.878/2025 |

**Caveat — secondary source for targets.** No Ministry document found during F02-T03 lists every
target in one table; the CNM study is a secondary source that cites the national calendar.
The reconciliation with the official panel (F06-T06) checks these values.

**Caveat — age granularity.** The open data has age in whole years only (`nu_idade_paciente`),
not birth dates, so the age limits in months (e.g. rotavirus 1st dose up to 11 months and 29
days) can only be approximated, and Hepatitis B at birth (≤ 30 days) cannot be computed
(`computable = false`). The methodology (F06-T03) documents the approximation.

## Updating

- New vaccine or dose codes: re-run `build_code_seeds.py` on recent samples and review the diff.
- New calendar or targets: edit `coverage_indicators.csv` in a PR that cites the new document.
