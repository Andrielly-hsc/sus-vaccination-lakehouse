# ADR-0010: WSL2 for development, dev container for visitors

- **Status:** Accepted
- **Date:** 2026-11-25
- **Supersedes:** [ADR-0007](0007-github-codespaces-dev-environment.md)

## Context

ADR-0007 chose GitHub Codespaces as the development environment. Before any real work was done in it, two facts changed the trade-off:

1. **Iteration speed.** Development is done together with an AI coding assistant running on the author's laptop. In a codespace, Spark code can only be executed through CI (about one minute per round trip). Locally, tests run in seconds. The data features (ingestion, streaming, MERGE, skew experiments) need many short iterations.
2. **What visitors need is independent of where the author develops.** Reviewers read the README, look at the green CI badge and, if they want to run the project, click *Open in Codespaces* — which runs on **their own** Codespaces quota, not the author's. The dev container serves them whatever the author uses.

WSL2 costs a one-time installation (admin rights, a reboot) and shares the laptop's 8 GB RAM with Windows, which is manageable by capping WSL's memory.

## Decision

- **Development** runs in **WSL2 Ubuntu 24.04** with **Temurin/OpenJDK 17** and **Python 3.11** (deadsnakes PPA), set up by `scripts/wsl_setup.sh`.
  - The repository stays on the Windows drive (`/mnt/d/...`), so it can be edited from Windows tools; the **virtual environment and all data** (`data_dir`, Delta tables, checkpoints) live in the Linux filesystem (`~/.venvs/vaxlake`, `~/vaxlake-data`), where I/O is fast.
  - WSL memory is capped at 5 GB in `%UserProfile%\.wslconfig`; the Spark driver uses at most 3 GB.
  - Git is run from one side only (Windows), so file-mode and line-ending differences never appear.
- **The dev container stays** (`.devcontainer/`) with the *Open in GitHub Codespaces* badge, as the zero-install way for visitors to run the project. CI keeps the same Java and Python versions.
- Native Windows remains unsupported for Spark.

## Consequences

- + Spark tests and pipeline runs execute locally in seconds; no quota limits
- + Works offline; no dependency on Codespaces billing
- + Visitors keep a one-click environment; the dev container remains the executable documentation of the environment
- − One-time installation that only the author can do (admin rights, Linux password)
- − 8 GB shared with Windows: heavy runs (full backfill) must close other applications or temporarily raise the WSL cap
- − Two environments to keep consistent (WSL2 and dev container) — mitigated because both pin the same Java/Python versions and install the same lock file, and CI checks the result
