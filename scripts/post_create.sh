#!/usr/bin/env bash
# Runs once when the dev container / codespace is created (see .devcontainer/devcontainer.json).
# Safe to re-run by hand: every step is idempotent.
set -euo pipefail

echo "==> Java and Python"
java -version 2>&1 | head -n 1
python --version

echo "==> Python dependencies"
python -m pip install --upgrade pip --quiet
if [[ -f requirements-lock.txt ]]; then
    # Exact, reproducible versions. The container is already isolated, so no virtualenv is needed.
    python -m pip install -r requirements-lock.txt --quiet
    python -m pip install -e . --no-deps --quiet
else
    echo "requirements-lock.txt not found yet (created in F01-T03) - skipping."
fi

echo "==> Git hooks"
if command -v pre-commit >/dev/null 2>&1 && [[ -f .pre-commit-config.yaml ]]; then
    pre-commit install
fi

# Local folders for data, Delta tables and checkpoints (git-ignored).
mkdir -p data

echo "==> Ready. Try: pytest"
