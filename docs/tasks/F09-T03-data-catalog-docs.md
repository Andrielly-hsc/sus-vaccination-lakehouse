# F09-T03 — Generate catalog documentation

| Field | Value |
|---|---|
| **Feature** | [F09 — Catalog, lineage & governance](../features/F09-catalog-lineage-governance.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F09-T01](F09-T01-metastore-catalog.md) |
| **Branch** | `feat/F09-T03-data-catalog-docs` |

## Description

One Markdown page per table generated from contracts plus live statistics.

## Steps

1. Template: description, owner, grain, columns, quality rules, freshness, row count, last update
2. `vaxlake docs` writes `docs/catalog/<layer>/<table>.md` and an index
3. Link from README

## Acceptance criteria

- [ ] Every table has a catalog page

## Deliverables

- `src/vaccination_lakehouse/governance/catalog_docs.py`
- `docs/catalog/`

## Why this matters (best practice)

'Docs as code' keeps documentation reviewable in PRs and always in sync with contracts — the same idea as dbt docs or Data Contract CLI exports.

## Notes

_Add decisions, problems found and links to the PR here while working._
