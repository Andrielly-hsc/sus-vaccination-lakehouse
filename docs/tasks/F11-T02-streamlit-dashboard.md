# F11-T02 — Build the Streamlit dashboard

| Field | Value |
|---|---|
| **Feature** | [F11 — Accountability dashboard](../features/F11-accountability-dashboard.md) |
| **Status** | To Do |
| **Estimate** | 4 h |
| **Depends on** | [F11-T01](F11-T01-serving-layer.md) |
| **Branch** | `feat/F11-T02-streamlit-dashboard` |

## Description

Pages for coverage, dropout, timeliness and live doses.

## Steps

1. Coverage page: municipality table/map vs target, homogeneity by UF
2. Dropout page with PNI classes
3. Timeliness page: lag ranking by municipality and facility
4. Live page: hourly doses refreshing during a replay
5. Colour-blind-safe palette; insight-stating titles

## Acceptance criteria

- [ ] All pages load in < 3 s on the dev scope
- [ ] Screenshot in README

## Deliverables

- `dashboard/app.py`
- `dashboard/pages/`

## Why this matters (best practice)

A dashboard is a product: every chart answers a question from §1.1. Consistent visual standards make it credible.

## Notes

_Add decisions, problems found and links to the PR here while working._
