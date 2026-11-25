# F02-T06 — LGPD privacy assessment

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | To Do |
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

- [ ] `privacy_assessment.md` lists each rule and the task that implements it

## Deliverables

- `docs/data/privacy_assessment.md`

## Why this matters (best practice)

Even 'anonymised' open data can be re-identified when combined. Privacy-by-design (minimisation + disclosure control) is required by LGPD/GDPR and is exactly what a public-sector data team is expected to demonstrate.

## Notes

_Add decisions, problems found and links to the PR here while working._
