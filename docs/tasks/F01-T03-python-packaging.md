# F01-T03 — Package the project and pin Spark/Delta

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | Done |
| **Estimate** | 1.5 h |
| **Depends on** | [F01-T02](F01-T02-dev-environment.md) |
| **Branch** | `feat/F01-T03-python-packaging` |

## Description

PEP 621 packaging with a `src/` layout and a lock file containing a compatible Spark/Delta pair.

## Steps

1. Create `pyproject.toml` (hatchling) with package `vaccination_lakehouse` and console script `vaxlake`
2. Choose Spark 4.x and the matching `delta-spark` from the Delta compatibility table; record them in an ADR note
3. Generate `requirements-lock.txt` with pip-tools (`pip-compile --extra dev`)
4. Add `vaxlake --version`

## Acceptance criteria

- [ ] `pip install -r requirements-lock.txt && pip install -e .` works in a clean venv
- [ ] `vaxlake --version` prints the version

## Deliverables

- `pyproject.toml`
- `requirements-lock.txt`
- `src/vaccination_lakehouse/__init__.py`
- `src/vaccination_lakehouse/cli.py`

## Why this matters (best practice)

Loose ranges in `pyproject.toml` declare compatibility; the lock file makes builds reproducible. For Spark the pin matters even more: Delta Lake only works with specific Spark versions, and a silent upgrade breaks the session at start-up.

## Notes

- PySpark 4.1.4 + delta-spark 4.4.1 ([ADR-0009](../adr/0009-spark-and-delta-version-pins.md)). delta-spark 4.4 allows Spark ≤ 4.2 and Great Expectations' Spark extra requires < 4.2, hence 4.1.
- Delta ≥ 4.1 names its JAR with the Spark version (`io.delta:delta-spark_4.1_2.13`); `configure_spark_with_delta_pip()` picks it automatically.
- Lock compiled with pip-tools on Python 3.11. It contains `colorama` (a Windows-only dependency of click/pytest) because it was compiled on Windows; harmless on Linux.
- Windows-only pitfall found: Python 3.11 reads `.pth` files with the locale encoding, so an editable install fails when the path has non-ASCII characters (`Portifólio`). Irrelevant in WSL2, Codespaces and CI, where Linux decodes paths as UTF-8; it only affects the Windows venv used for quick lint/unit checks.
