# F07-T05 — Test the quality gates

| Field | Value |
|---|---|
| **Feature** | [F07 — Data quality with Great Expectations](../features/F07-data-quality-great-expectations.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F07-T03](F07-T03-quality-gates-in-pipeline.md) |
| **Branch** | `feat/F07-T05-quality-tests` |

## Description

Prove each critical expectation fails on purpose-built bad fixtures.

## Steps

1. Fixtures with duplicate ids, future dates, invalid municipality, missing columns
2. Assert the gate fails with the expected expectation
3. Assert warnings do not block

## Acceptance criteria

- [ ] Every critical expectation has a failing-fixture test

## Deliverables

- `tests/integration/test_quality_gates.py`

## Why this matters (best practice)

A test that never fails proves nothing. Testing the tests (negative fixtures) is how you know a gate actually protects you.

## Notes

_Add decisions, problems found and links to the PR here while working._
