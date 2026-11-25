# F02-T02 — Write the data dictionary

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | Done |
| **Estimate** | 3 h |
| **Depends on** | [F02-T01](F02-T01-source-discovery.md) |
| **Branch** | `feat/F02-T02-data-dictionary` |

## Description

Map each source column to an English name, type, domain and meaning, and decide what we keep.

## Steps

1. For each column: source name, English `snake_case` name, target type, nullability, domain/allowed values, description
2. Classify each column: identifier / quasi-identifier / sensitive / operational
3. Mark columns dropped in silver (minimisation) and why
4. Document code systems: vaccine codes, dose descriptions, race/colour, sex, establishment type

## Acceptance criteria

- [x] Every source column appears in the dictionary with a keep/drop decision

## Deliverables

- `docs/data/data_dictionary.md`
- `scripts/discovery/code_values.py` (code systems and consistency checks)

## Why this matters (best practice)

Renaming to a consistent English vocabulary once, in a documented table, is what makes downstream code readable. Classifying identifiers early drives privacy decisions instead of retro-fitting them.

## Notes

- Based on 300 000 sample rows (first 200 000 of Jan/2025 + first 100 000 of Jun/2025, a campaign month), read with HTTP Range requests (50 MB instead of 4.9 GB).
- **35 columns kept, 21 dropped**: 10 sensitive (racial/ethnic origin, pregnancy, priority groups such as comorbidities), 5 redundant with reference data, 6 not needed. Bronze still keeps all 56 as strings, so a later need can be met by rebuilding silver.
- The silver names follow the CSV, not the PDF: 8 columns have different names in the PDF (see sources.md §1.4).
- Codes stay strings (leading zeros). Every code maps to a single description except one `co_sistema_origem` (a per-installation code with free-text names).
- Surprises: no birth date in the file, only `nu_idade_paciente` in whole years; `nu_cep_paciente` is a 5-digit CEP prefix; 3 rows with a 14-character CNES and no facility municipality; replacements (`co_troca_documento`) point to documents in earlier files.
- `patient_key` (pseudonymous RNDS hash) is kept in silver only, for duplicate detection; final decision in F02-T06.
