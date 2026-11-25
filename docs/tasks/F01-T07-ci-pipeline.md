# F01-T07 — GitHub Actions CI with Java 17

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F01-T04](F01-T04-code-quality-tooling.md), [F01-T06](F01-T06-test-scaffolding.md) |
| **Branch** | `feat/F01-T07-ci-pipeline` |

## Description

CI that lints, runs unit and Spark tests on Ubuntu with cached dependencies.

## Steps

1. Workflow: lint (pre-commit) → unit → spark tests; `permissions: contents: read`, concurrency cancel
2. `actions/setup-java` (Temurin 17) + `actions/setup-python` (3.11, pip cache)
3. Cache `~/.ivy2` so Delta/OpenLineage jars are downloaded once
4. CI badge in README

## Acceptance criteria

- [ ] CI green on the PR
- [ ] Second run is faster thanks to caches

## Deliverables

- `.github/workflows/ci.yml`

## Why this matters (best practice)

CI is the referee: `main` is only as trustworthy as the checks that guard it. Least-privilege permissions and caching are part of a professional workflow, not extras.

## Notes

_Add decisions, problems found and links to the PR here while working._
