# F11-T03 — Communicate methodology and uncertainty

| Field | Value |
|---|---|
| **Feature** | [F11 — Accountability dashboard](../features/F11-accountability-dashboard.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F11-T02](F11-T02-streamlit-dashboard.md) |
| **Branch** | `feat/F11-T03-indicator-communication` |

## Description

Make caveats visible where numbers are read.

## Steps

1. Methodology panel per indicator (numerator, denominator, source vintage)
2. Badges: provisional (real-time), suppressed, coverage > 100 %
3. Link to data card and reconciliation

## Acceptance criteria

- [ ] Every indicator shows its definition and data date

## Deliverables

- `dashboard/components/methodology.py`

## Why this matters (best practice)

Public indicators are misread without context. Showing denominators, data dates and provisional status is part of responsible publishing.

## Notes

_Add decisions, problems found and links to the PR here while working._
