# F01-T02 — Set up the Codespaces dev container

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | In Review |
| **Estimate** | 3 h |
| **Depends on** | [F01-T01](F01-T01-initialize-repository.md) |
| **Branch** | `feat/F01-T02-codespaces-dev-environment` |

## Description

Define the development environment as code: a dev container that GitHub Codespaces builds with Java 17, Python 3.11 and the project installed.

## Steps

1. Add `.devcontainer/devcontainer.json`: image `mcr.microsoft.com/devcontainers/python` (3.11), feature `ghcr.io/devcontainers/features/java` (17), `hostRequirements` 2 cores / 8 GB
2. `postCreateCommand` runs `scripts/post_create.sh`: installs `requirements-lock.txt` and the package once they exist (F01-T03), then `pre-commit install`; set `JAVA_HOME` and `PYSPARK_PYTHON`
3. VS Code customisations: Python, Ruff, Jupyter, YAML extensions; forward port 4040 (Spark UI) and 8501 (Streamlit)
4. Set the idle timeout to 30 min in GitHub settings and document the free quota (core-hours, 15 GB storage) and how to check usage
5. Write `docs/setup.md`: create/stop/delete a codespace, open the Spark UI, where data lives, common errors (out of memory, quota)

## Acceptance criteria

- [ ] A new codespace opens with `java -version` = 17 and Python 3.11 with no manual step; once F01-T03 adds the lock file, `pyspark --version` also works on a fresh codespace
- [ ] Spark UI reachable on the forwarded port 4040 during a job
- [ ] `docs/setup.md` lets someone else reproduce the environment from the repository page

## Deliverables

- `.devcontainer/devcontainer.json`
- `docs/setup.md`

## Why this matters (best practice)

Dev containers are the industry standard for reproducible environments: the setup guide becomes executable code, identical for every developer and reviewer. Treating cloud quota (core-hours, storage) as a resource to manage is also part of working with cloud development environments.

## Notes

- Image `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` + feature `java:1` (Temurin 17, same JDK as CI).
- `postCreateCommand` → `scripts/post_create.sh` (idempotent; installs the lock file, the package and the git hooks).
- Not yet verified in a real codespace: the author opens the first one after this PR is merged. The idle timeout (30 min) is a personal GitHub setting, documented in `docs/setup.md`.
