# F06-T04 — Compute dropout and homogeneity

| Field | Value |
|---|---|
| **Feature** | [F06 — Gold layer — vaccination indicators](../features/F06-gold-vaccination-indicators.md) |
| **Status** | To Do |
| **Estimate** | 2.5 h |
| **Depends on** | [F06-T03](F06-T03-coverage-indicator.md) |
| **Branch** | `feat/F06-T04-dropout-and-homogeneity` |

## Description

Dropout rate per multi-dose vaccine and homogeneity of coverage among municipalities.

## Steps

1. `ind_dropout_yearly`: (D1 − last dose)/D1 with PNI classes low/medium/high
2. `ind_homogeneity_yearly`: % of municipalities in a UF meeting the target per vaccine
3. Tests with fixtures; document caveats (people moving between municipalities)

## Acceptance criteria

- [ ] Classes match PNI thresholds
- [ ] Fixture tests pass

## Deliverables

- `src/vaccination_lakehouse/gold/dropout.py`
- `tests/spark/test_dropout.py`

## Why this matters (best practice)

Coverage alone hides *where* schedules break. Dropout and homogeneity are the standard PNI lenses for equity and follow-up failures.

## Notes

_Add decisions, problems found and links to the PR here while working._
