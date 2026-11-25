# F01-T02 — Set up WSL2 and the dev container

| Field | Value |
|---|---|
| **Feature** | [F01 — Project setup & engineering standards](../features/F01-project-setup.md) |
| **Status** | In Review |
| **Estimate** | 3 h |
| **Depends on** | [F01-T01](F01-T01-initialize-repository.md) |
| **Branch** | `feat/F01-T02-codespaces-dev-environment`, then `feat/F01-T02-wsl2-dev-environment` |

## Description

Two reproducible Linux environments with the same Java and Python versions: **WSL2 Ubuntu** for
day-to-day development on the laptop, and a **dev container** that gives visitors a one-click
GitHub Codespaces environment ([ADR-0010](../adr/0010-wsl2-for-development-dev-container-for-visitors.md)).

## Steps

1. Add `.devcontainer/devcontainer.json`: image `mcr.microsoft.com/devcontainers/python` (3.11), feature `ghcr.io/devcontainers/features/java` (17), `hostRequirements` 2 cores / 8 GB, ports 4040 (Spark UI) and 8501 (Streamlit)
2. `postCreateCommand` runs `scripts/post_create.sh` (installs the lock file, the package and the git hooks)
3. Write `scripts/wsl_setup.sh`: OpenJDK 17 + Python 3.11 (deadsnakes), venv in `~/.venvs/vaxlake`, data in `~/vaxlake-data`, `JAVA_HOME` and `vaxenv` in `~/.bashrc`; idempotent
4. Document the WSL2 installation (`wsl --install`), the memory cap in `.wslconfig`, where code/venv/data live and why, and the "git on Windows only" rule
5. Write `docs/setup.md` covering both environments and common errors

## Acceptance criteria

- [ ] In WSL2, after `bash scripts/wsl_setup.sh`: `java -version` = 17, `pytest` runs **without skipped Spark tests**, `vaxlake smoke-test` passes
- [ ] A new codespace opens with Java 17 and Python 3.11 and the project installed, with no manual step
- [ ] `docs/setup.md` lets someone else reproduce either environment

## Deliverables

- `.devcontainer/devcontainer.json`
- `scripts/post_create.sh`
- `scripts/wsl_setup.sh`
- `docs/setup.md`

## Why this matters (best practice)

A development environment that is written down as code (a setup script, a dev container) is
reproducible, reviewable and identical for everyone; one that lives only in someone's memory is
not. Keeping development close to production (Linux, same Java and Python versions, same lock
file, checked by CI) avoids "works on my machine". Choosing the environment by the team's real
workflow — here, fast local iterations — instead of by fashion is part of the decision.

## Notes

- First version chose Codespaces for development ([ADR-0007](../adr/0007-github-codespaces-dev-environment.md)). Before any work was done in it, the author switched to **WSL2** ([ADR-0010](../adr/0010-wsl2-for-development-dev-container-for-visitors.md)): Spark can then run locally in seconds instead of only through CI, with no quota. The dev container stays for visitors, who use their own Codespaces quota.
- Code stays on `D:` (edited from Windows); the venv and all data live on the Linux filesystem because Spark I/O through `/mnt/d` is several times slower.
- Git hooks are installed from Windows only; a hook installed from WSL would point to a Linux Python and break Windows commits.
- Pending verification: the author installs WSL2 (admin rights, reboot, Linux password), then runs the setup script; the dev container is checked the first time a codespace is opened.
