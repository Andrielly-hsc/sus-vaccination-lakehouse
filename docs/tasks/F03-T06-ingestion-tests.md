# F03-T06 — Test the ingestion layer

| Field | Value |
|---|---|
| **Feature** | [F03 — Batch ingestion into bronze](../features/F03-batch-ingestion-bronze.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F03-T04](F03-T04-incremental-idempotent-ingestion.md), [F03-T05](F03-T05-reference-data-ingestion.md) |
| **Branch** | `feat/F03-T06-ingestion-tests` |

## Description

Integration tests on fixtures that prove idempotency, failure recovery and reconciliation.

## Steps

1. Hand-made fixture CSVs (fictitious values) incl. a malformed row and a wrong-encoding file
2. Tests: run twice → same count; kill/restart; corrupt rows isolated; manifest = bronze
3. Mark as `integration`

## Acceptance criteria

- [ ] All ingestion tests pass in CI

## Deliverables

- `tests/fixtures/sipni/`
- `tests/integration/test_ingestion.py`

## Why this matters (best practice)

Idempotency is a claim until it is tested. Tests that re-run and interrupt the pipeline turn reliability into evidence.

## Notes

_Add decisions, problems found and links to the PR here while working._
