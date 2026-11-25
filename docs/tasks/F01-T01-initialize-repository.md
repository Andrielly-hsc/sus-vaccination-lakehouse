# F01-T01 — Initialise repository conventions

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | Done |
| **Estimate** | 1 h |
| **Depends on** | — |
| **Branch** | `feat/F01-T01-initialize-repository` |

## Description

Complete the repository skeleton created with the docs: ignore rules, line endings, PR template and branch rules.

## Steps

1. Review `.gitignore` (data/, checkpoints, metastore, spark-warehouse, derby.log, .venv) and `.gitattributes` (LF)
2. Add `.editorconfig` and `.github/pull_request_template.md` (task ID, what/why, how to verify, checklist)
3. Protect `main` on GitHub: PRs required, CI must pass, no force-push
4. Write `CHANGELOG.md` (Keep a Changelog) with an *Unreleased* section

## Acceptance criteria

- [ ] `git status` is clean after running the pipeline (no data or Spark artefacts tracked)
- [ ] Branch protection active on `main`

## Deliverables

- `.gitignore`
- `.gitattributes`
- `.editorconfig`
- `.github/pull_request_template.md`
- `CHANGELOG.md`

## Why this matters (best practice)

Spark leaves many local artefacts (`spark-warehouse/`, `metastore_db/`, `derby.log`, checkpoints). Ignoring them from day one avoids committing gigabytes or machine-specific state — a classic first-week mistake.

## Notes

- Initial docs commit went straight to `main` (bootstrap); from here every task has its own branch, merged into `feat/F01-project-setup`, and one PR per feature.
- **Branch protection** enabled after PR #1 merged: PR required (0 approvals, solo project), `Lint (pre-commit)` and `Tests (unit + Spark)` must pass on an up-to-date branch, conversations resolved, no force-push or deletion, enforced for admins too.
- `.gitignore` already covered Spark artefacts (`spark-warehouse/`, `metastore_db/`, `derby.log`); the SparkSession also points Derby to `data/metastore` so nothing lands in the repo root.
