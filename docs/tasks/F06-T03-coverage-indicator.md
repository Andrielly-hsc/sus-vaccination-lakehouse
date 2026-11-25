# F06-T03 — Compute vaccination coverage

| Field | Value |
|---|---|
| **Feature** | [F06 — Gold layer — vaccination indicators](../features/F06-gold-vaccination-indicators.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F06-T02](F06-T02-incremental-gold-with-cdf.md), [F03-T05](F03-T05-reference-data-ingestion.md) |
| **Branch** | `feat/F06-T03-coverage-indicator` |

## Description

Coverage per municipality × vaccine × year vs PNI target, following the Ministry's methodology.

## Steps

1. Write `docs/data/indicator_methodology.md`: numerator (dose completing schedule, age group, residence municipality), denominator (SINASC), targets
2. Implement `gold.ind_coverage_yearly` with `coverage_pct`, `target_pct`, `meets_target`
3. Apply small-cell suppression (`is_suppressed`) per privacy rules
4. Unit tests on a hand-calculated example

## Acceptance criteria

- [ ] Hand-calculated fixture matches
- [ ] Coverage > 100 % is reported with a flag, not capped

## Deliverables

- `src/vaccination_lakehouse/gold/coverage.py`
- `docs/data/indicator_methodology.md`
- `tests/spark/test_coverage.py`

## Why this matters (best practice)

Accountability depends on computing the indicator exactly as the official methodology says — and documenting it so anyone can recompute it. Transparent methodology is worth more than a pretty chart.

## Notes

_Add decisions, problems found and links to the PR here while working._
