# F01-T06 — Test scaffolding with a shared Spark fixture

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | Done |
| **Estimate** | 1.5 h |
| **Depends on** | [F01-T05](F01-T05-spark-session-and-config.md) |
| **Branch** | `feat/F01-T06-test-scaffolding` |

## Description

pytest layout, markers and a fast session-scoped SparkSession for tests.

## Steps

1. Create `tests/unit`, `tests/spark`, `tests/integration`, `tests/fixtures`
2. `conftest.py`: session-scoped `spark` fixture (`local[2]`, `spark.sql.shuffle.partitions=2`, UI off, temp warehouse)
3. Markers `spark` and `integration`; coverage with pytest-cov
4. First tests: config loads; Delta round-trip; `assertDataFrameEqual` example

## Acceptance criteria

- [ ] `pytest -m 'not spark'` runs in seconds
- [ ] `pytest` (all) passes locally

## Deliverables

- `tests/conftest.py`
- `tests/unit/test_config.py`
- `tests/spark/test_delta_smoke.py`

## Why this matters (best practice)

Starting a JVM per test makes a Spark suite unusable. One session per run with tiny shuffle partitions is the standard pattern; markers let developers run the fast subset constantly and the slow one before pushing.

## Notes

- Tests run with the `ci` profile. Tests using the `spark` fixture get the `spark` marker automatically; without Java they are **skipped locally with a visible reason, but never in CI** (`CI=true`).
- Includes a miniature MERGE idempotency test — the core promise of the silver layer.
- Local run (Windows, no Java): 22 passed, 3 Spark tests skipped, 85 % coverage.
- In WSL2 the 3 Spark tests took 60 s, mostly Delta's log replay with 50 partitions per tiny table. Setting `spark.databricks.delta.snapshotPartitions` to 2 in the `ci` profile (8 in `base`) brought the **whole suite to 46 s** (MERGE 20 s -> 6 s, measured).
