# F01-T05 — SparkSession factory, config profiles and logging

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F01-T03](F01-T03-python-packaging.md) |
| **Branch** | `feat/F01-T05-spark-session-and-config` |

## Description

One place that builds a Delta-enabled SparkSession and one validated configuration object.

## Steps

1. `spark.py`: `get_spark(app_name, conf)` with Delta extensions/catalog, `configure_spark_with_delta_pip`, AQE on, time zone `America/Sao_Paulo`, driver memory from config
2. `config.py`: pydantic-settings model loading `conf/base.yaml` + profile (`dev`, `ci`) + `VAXLAKE_*` env vars
3. Config holds scope (UFs, months), paths (landing, lakehouse, checkpoints), thresholds (watermark, suppression)
4. `logging_setup.py`: JSON logs with run_id; quiet Spark/py4j loggers
5. Add `.env.example`

## Acceptance criteria

- [ ] A smoke script writes and reads a Delta table using `get_spark()`
- [ ] Invalid config (e.g. unknown UF) fails at start-up with a clear message

## Deliverables

- `src/vaccination_lakehouse/spark.py`
- `src/vaccination_lakehouse/config.py`
- `src/vaccination_lakehouse/logging_setup.py`
- `conf/base.yaml`
- `conf/dev.yaml`
- `conf/ci.yaml`
- `.env.example`

## Why this matters (best practice)

Duplicated `SparkSession.builder` code across jobs, tests and notebooks drifts and causes 'works in the notebook, fails in the job'. Validating configuration at start-up (fail fast) is far cheaper than discovering a typo after an hour of processing.

## Notes

_Add decisions, problems found and links to the PR here while working._
