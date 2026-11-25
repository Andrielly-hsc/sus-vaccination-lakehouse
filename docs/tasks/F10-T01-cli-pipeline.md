# F10-T01 — CLI for every pipeline step

| Field | Value |
|---|---|
| **Feature** | [F10 — Pipeline orchestration & operations](../features/F10-orchestration-and-operations.md) |
| **Status** | To Do |
| **Estimate** | 2.5 h |
| **Depends on** | [F06-T02](F06-T02-incremental-gold-with-cdf.md) |
| **Branch** | `feat/F10-T01-cli-pipeline` |

## Description

Typer commands with shared options and a `run-all` that respects dependencies.

## Steps

1. Commands: download, reference, ingest, replay, stream, silver, gold, quality, optimize, docs, audit
2. Global options: `--profile`, `--months`, `--ufs`, `--dry-run`
3. `run-all` in dependency order, stopping on gate failures
4. `--help` texts reviewed

## Acceptance criteria

- [ ] Every command documented by `--help` and in README

## Deliverables

- `src/vaccination_lakehouse/cli.py`

## Why this matters (best practice)

A CLI is the contract between the code and its operators (or an orchestrator later). Airflow/Dagster tasks would call exactly these commands.

## Notes

_Add decisions, problems found and links to the PR here while working._
