# F02-T06 — LGPD privacy assessment

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | Done |
| **Estimate** | 2 h |
| **Depends on** | [F02-T02](F02-T02-data-dictionary.md) |
| **Branch** | `feat/F02-T06-privacy-assessment` |

## Description

Assess re-identification risk and define the minimisation and disclosure-control rules the pipeline enforces.

## Steps

1. Describe the legal context: health data as sensitive personal data (LGPD art. 5 II, art. 11); anonymised data (art. 12); public-interest use
2. Identify quasi-identifiers (birth date, sex, race/colour, residence municipality) and risky combinations in small municipalities
3. Define rules: drop/aggregate fields in silver (e.g. birth date → age in months), no patient hash in gold, small-cell suppression threshold (default < 5)
4. Define what may be published in the dashboard and README

## Acceptance criteria

- [x] `privacy_assessment.md` lists each rule and the task that implements it (P1–P11)

## Deliverables

- `docs/data/privacy_assessment.md`
- `scripts/discovery/reidentification_risk.py`
- `privacy.suppression_threshold` in `conf/base.yaml` / `config.py`

## Why this matters (best practice)

Even 'anonymised' open data can be re-identified when combined. Privacy-by-design (minimisation + disclosure control) is required by LGPD/GDPR and is exactly what a public-sector data team is expected to demonstrate.

## Notes

- The plan assumed a birth date to coarsen; the file has none (age in whole years), so the main minimisation is dropping columns (P1) and keeping the pseudonym out of gold (P3).
- **Measured** re-identification risk with k-anonymity on 300 000 sample rows: municipality alone 0 % unique, municipality + age + sex 23 %, municipality + date + age + sex 69 %, CEP prefix + date + age + sex 89 %. Upper bounds (sample), but they justify keeping record-level data inside the lakehouse.
- Suppression covers the **complement** too: a coverage of 7/8 reveals the one unvaccinated child, so the rule also checks target population − vaccinated.
- Legal context written for LGPD with the GDPR equivalents next to it (relevant for an EU employer). Technical assessment, not legal advice.
- The threshold is configuration (`privacy.suppression_threshold`, minimum 3), validated and tested, so gold (F06) and the dashboard (F11) read the same value.
