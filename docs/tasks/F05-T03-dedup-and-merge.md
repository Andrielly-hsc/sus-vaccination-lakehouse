# F05-T03 — Deduplicate and MERGE into silver

| Field | Value |
|---|---|
| **Feature** | [F05 — Silver layer — cleaned, validated, conformed](../features/F05-silver-layer.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F05-T02](F05-T02-validation-and-quarantine.md) |
| **Branch** | `feat/F05-T03-dedup-and-merge` |

## Description

Idempotent upsert of valid rows into `silver.vaccination_doses` from `foreachBatch`.

## Steps

1. Within a micro-batch keep the latest version per `dose_id` (window by registration time)
2. `MERGE INTO … ON dose_id WHEN MATCHED AND source newer THEN UPDATE WHEN NOT MATCHED THEN INSERT`
3. Use Delta `txnAppId`/`txnVersion` so a retried batch is a no-op
4. Enable Change Data Feed and partition by `vaccination_month`; contract comments applied

## Acceptance criteria

- [ ] Running the same batch twice changes nothing (test)
- [ ] Duplicates injected by the replayer are removed

## Deliverables

- `src/vaccination_lakehouse/silver/merge.py`
- `tests/integration/test_silver_merge.py`

## Why this matters (best practice)

MERGE on a business key is the backbone of idempotent lakehouse pipelines. Delta's transaction identifiers close the last gap: a micro-batch retried after a crash cannot be applied twice.

## Notes

_Add decisions, problems found and links to the PR here while working._
