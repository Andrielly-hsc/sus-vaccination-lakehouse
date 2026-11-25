# F01-T04 — Configure ruff and pre-commit

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | In Review |
| **Estimate** | 1 h |
| **Depends on** | [F01-T03](F01-T03-python-packaging.md) |
| **Branch** | `feat/F01-T04-code-quality-tooling` |

## Description

One linter/formatter and git hooks so style never reaches code review.

## Steps

1. Configure ruff (line length 100, rules E, F, I, B, UP, SIM) in `pyproject.toml`
2. Add `.pre-commit-config.yaml` (whitespace, YAML/TOML checks, large files, ruff check/format)
3. Run `pre-commit install` and fix the initial findings

## Acceptance criteria

- [ ] `pre-commit run --all-files` passes

## Deliverables

- `.pre-commit-config.yaml`
- `pyproject.toml ([tool.ruff])`

## Why this matters (best practice)

Automated formatting ends style discussions; hooks catch problems before CI, keeping the feedback loop seconds instead of minutes.

## Notes

- `ruff format` also formats Python code blocks inside Markdown: the ARCHITECTURE example was rewritten with `withColumns({...})` so it stays readable (and documents a real best practice).
- Added `detect-private-key` hook; `check-added-large-files` at 500 kB keeps data out of git.
