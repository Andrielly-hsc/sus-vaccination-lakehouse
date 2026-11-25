# F06-T06 — Reconcile with official figures

| Field | Value |
|---|---|
| **Feature** | [F06 — Gold layer — vaccination indicators](../features/F06-gold-vaccination-indicators.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F06-T03](F06-T03-coverage-indicator.md) |
| **Branch** | `feat/F06-T06-reconciliation-with-official-panel` |

## Description

Compare our coverage with the Ministry's published panel for sample municipalities.

## Steps

1. Pick ~10 municipalities (large, medium, small) and 3 vaccines for one year
2. Collect official values (panel/TabNet) with access date
3. Compute differences; explain each (data vintage, denominators, residence vs facility)
4. Publish `docs/data/reconciliation.md`

## Acceptance criteria

- [ ] Every difference above 2 pp has a documented explanation

## Deliverables

- `docs/data/reconciliation.md`

## Why this matters (best practice)

Reconciliation with an authoritative source is how a new pipeline earns trust. Explaining differences openly is better than tuning code until numbers 'look right'.

## Notes

_Add decisions, problems found and links to the PR here while working._
