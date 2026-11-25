# F07-T03 — Run quality gates inside the pipeline

| Field | Value |
|---|---|
| **Feature** | [F07 — Data quality with Great Expectations](../features/F07-data-quality-great-expectations.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F07-T02](F07-T02-expectation-suites.md) |
| **Branch** | `feat/F07-T03-quality-gates-in-pipeline` |

## Description

Validate after each layer's write candidate; block on critical failures; persist results.

## Steps

1. Validation definitions/checkpoints per layer
2. Critical failure → raise `QualityGateError`, skip downstream steps, keep previous good version
3. Persist every result in `ops.quality_results` (run_id, table, expectation, success, observed value)
4. Add Delta `CHECK` constraints for hard invariants (`doses >= 0`)

## Acceptance criteria

- [ ] Injecting invalid data stops the pipeline at the right layer (test)
- [ ] Results queryable per run

## Deliverables

- `src/vaccination_lakehouse/quality/gates.py`

## Why this matters (best practice)

'Write-audit-publish': validate before consumers can see data. Gates that block publication are the difference between monitoring quality and guaranteeing it.

## Notes

_Add decisions, problems found and links to the PR here while working._
