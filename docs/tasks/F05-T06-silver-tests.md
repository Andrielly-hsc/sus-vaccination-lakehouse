# F05-T06 — Silver reconciliation tests

| Field | Value |
|---|---|
| **Feature** | [F05 — Silver layer — cleaned, validated, conformed](../features/F05-silver-layer.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F05-T04](F05-T04-streaming-silver-with-watermark.md), [F05-T05](F05-T05-establishment-dimension-scd2.md) |
| **Branch** | `feat/F05-T06-silver-tests` |

## Description

End-to-end checks bronze → silver on fixtures.

## Steps

1. Reconciliation: bronze = silver + quarantine + removed duplicates
2. Idempotency: full run twice → identical silver
3. Late event path test
4. Minimisation test: no dropped column reaches silver

## Acceptance criteria

- [ ] All silver tests pass in CI

## Deliverables

- `tests/integration/test_silver.py`

## Why this matters (best practice)

Reconciliation ('every row accounted for') is the auditor's question. Answering it with an automated test is a strong signal of engineering maturity.

## Notes

_Add decisions, problems found and links to the PR here while working._
