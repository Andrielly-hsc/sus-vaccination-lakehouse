# F02-T02 — Write the data dictionary

| Field | Value |
|---|---|
| **Feature** | [F02 — Source discovery & data contracts](../features/F02-source-discovery-and-data-contracts.md) |
| **Status** | To Do |
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

- [ ] Every source column appears in the dictionary with a keep/drop decision

## Deliverables

- `docs/data/data_dictionary.md`

## Why this matters (best practice)

Renaming to a consistent English vocabulary once, in a documented table, is what makes downstream code readable. Classifying identifiers early drives privacy decisions instead of retro-fitting them.

## Notes

_Add decisions, problems found and links to the PR here while working._
