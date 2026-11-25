# F01-T02 — Set up WSL2, Java 17 and a dev container

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | To Do |
| **Estimate** | 3 h |
| **Depends on** | [F01-T01](F01-T01-initialize-repository.md) |
| **Branch** | `feat/F01-T02-local-spark-environment` |

## Description

Create the Linux environment Spark expects, locally (WSL2) and in the cloud (Codespaces), and document it step by step.

## Steps

1. Install WSL2 + Ubuntu LTS (`wsl --install -d Ubuntu`); clone the repo inside the WSL filesystem (`~/projects/`)
2. Install OpenJDK 17 and Python 3.11 in Ubuntu; set `JAVA_HOME`
3. Create `.wslconfig` limiting WSL memory (e.g. 5 GB) so Windows stays responsive
4. Add `.devcontainer/devcontainer.json` (Python 3.11 image + Java 17 feature) for Codespaces
5. Write `docs/setup.md` with every command and common errors (JAVA_HOME, memory, `/mnt/d` slowness)

## Acceptance criteria

- [ ] `java -version` shows 17 and `python3.11 --version` works in WSL
- [ ] A Codespace opens and runs `pyspark --version`
- [ ] `docs/setup.md` lets someone else reproduce the setup

## Deliverables

- `docs/setup.md`
- `.devcontainer/devcontainer.json`
- `docs/adr/0007-local-spark-on-wsl2.md (status confirmed)`

## Why this matters (best practice)

Spark is developed and operated on Linux in virtually every company. A reproducible dev environment (dev containers are the industry standard for this) removes 'works on my machine' and lets reviewers run the project in one click.

## Notes

_Add decisions, problems found and links to the PR here while working._
