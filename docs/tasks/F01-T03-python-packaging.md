# F01-T03 — Package the project and pin Spark/Delta

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F01-T02](F01-T02-codespaces-dev-environment.md) |
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

_Add decisions, problems found and links to the PR here while working._
