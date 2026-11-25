# F09-T02 — Capture lineage with OpenLineage

| Field | Value |
|---|---|
| **Feature** | [F09 — Catalog, lineage & governance](../features/F09-catalog-lineage-governance.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F09-T01](F09-T01-metastore-catalog.md) |
| **Branch** | `feat/F09-T02-openlineage-integration` |

## Description

Spark listener emitting lineage events; script generating `docs/lineage.md`.

## Steps

1. Add `openlineage-spark` jar (version compatible with Spark 4) and file transport config
2. Run the pipeline; collect events in `data/lineage/`
3. `scripts/lineage_to_mermaid.py` → `docs/lineage.md`; `--check` mode in CI
4. (Could) `docker-compose` Marquez and screenshot

## Acceptance criteria

- [ ] Lineage graph shows every table from landing files to dashboard inputs
- [ ] CI fails if `lineage.md` is stale

## Deliverables

- `scripts/lineage_to_mermaid.py`
- `docs/lineage.md`

## Why this matters (best practice)

Automatic lineage answers 'what breaks if I change this?' and 'where did this number come from?'. OpenLineage is the open standard most catalogs ingest.

## Notes

_Add decisions, problems found and links to the PR here while working._
