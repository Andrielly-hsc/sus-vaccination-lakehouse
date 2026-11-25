# F01 — Project setup & engineering standards

| Field | Value |
|---|---|
| **Status** | In Review |
| **Priority** | Must (MoSCoW) |
| **Depends on** | — |
| **Estimate** | 12 h |
| **Created** | 2026-11-25 |

## Goal

A reproducible Linux-based Spark + Delta development environment, packaging, quality tooling and CI, so every later task starts from a green baseline.

## User story

> As a data engineer, I want one documented way to create the environment and run Spark tests locally and in CI, so that results never depend on my machine.

## Scope

**In scope**

- Repository conventions (branching, PR template, Conventional Commits)
- WSL2 development environment (Java 17 + Python 3.11) and a dev container for Codespaces, with a setup guide
- `pyproject.toml`, `src/` layout, pinned Spark/Delta compatible pair
- ruff + pre-commit
- SparkSession factory, YAML config profiles, JSON logging
- pytest with a session-scoped Spark fixture
- GitHub Actions CI with Java 17

**Out of scope**

- Cloud deployment (Fabric/Databricks) — documented as a migration path only
- Native Windows support (see ADR-0010)

## Acceptance criteria

- [ ] `pytest` runs a Spark + Delta smoke test green in WSL2 and in CI
- [ ] A fresh clone reaches a green test run by following `docs/setup.md` only (WSL2 or Codespaces)
- [ ] `pre-commit run --all-files` passes

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F01-T01](../tasks/F01-T01-initialize-repository.md) | Initialise repository conventions | 1 h | In Review |
| [F01-T02](../tasks/F01-T02-dev-environment.md) | Set up WSL2 and the dev container | 3 h | In Review |
| [F01-T03](../tasks/F01-T03-python-packaging.md) | Package the project and pin Spark/Delta | 1.5 h | In Review |
| [F01-T04](../tasks/F01-T04-code-quality-tooling.md) | Configure ruff and pre-commit | 1 h | In Review |
| [F01-T05](../tasks/F01-T05-spark-session-and-config.md) | SparkSession factory, config profiles and logging | 2 h | In Review |
| [F01-T06](../tasks/F01-T06-test-scaffolding.md) | Test scaffolding with a shared Spark fixture | 1.5 h | In Review |
| [F01-T07](../tasks/F01-T07-ci-pipeline.md) | GitHub Actions CI with Java 17 | 2 h | In Review |

## Syllabus topics covered

- 4.1 Python 3: modules, files, exceptions; modular organisation, tests, reproducibility
- Ops 1.1 Versioning of code · 1.3 Pipelines, tests, CI/CD · 1.4 Reproducibility
- Ops 2.4 Protection of secrets

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
