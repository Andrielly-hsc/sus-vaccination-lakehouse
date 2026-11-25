#!/usr/bin/env bash
# One-time setup of the WSL2 development environment (ADR-0010).
#
# Run inside Ubuntu (WSL2), from the repository folder on the Windows drive:
#     cd "/mnt/d/Pos_Ciencia-de-dados/Portifólio/sus-vaccination-lakehouse"
#     bash scripts/wsl_setup.sh
#
# Idempotent: safe to run again (e.g. after the lock file changes).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VAXLAKE_VENV:-$HOME/.venvs/vaxlake}"          # Linux filesystem: fast
DATA_DIR="${VAXLAKE_DATA_DIR:-$HOME/vaxlake-data}"    # Linux filesystem: fast
BASHRC="$HOME/.bashrc"

echo "==> System packages: Java 17 and Python 3.11 (asks for your Linux password)"
sudo apt-get update -qq
sudo apt-get install -y -qq software-properties-common
if ! apt-cache show python3.11 >/dev/null 2>&1; then
    # Ubuntu 24.04 ships Python 3.12; the deadsnakes PPA provides other versions.
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update -qq
fi
sudo apt-get install -y -qq openjdk-17-jdk-headless python3.11 python3.11-venv python3.11-dev

JAVA_HOME_DIR="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"

echo "==> Virtual environment in $VENV"
if [[ ! -x "$VENV/bin/python" ]]; then
    python3.11 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --upgrade pip --quiet
"$VENV/bin/python" -m pip install -r "$REPO/requirements-lock.txt" --quiet
"$VENV/bin/python" -m pip install -e "$REPO" --no-deps --quiet

echo "==> Data folder in $DATA_DIR"
mkdir -p "$DATA_DIR"

echo "==> Shell settings in $BASHRC"
if ! grep -q ">>> vaxlake >>>" "$BASHRC" 2>/dev/null; then
    cat >> "$BASHRC" <<EOF

# >>> vaxlake >>> (added by sus-vaccination-lakehouse/scripts/wsl_setup.sh)
export JAVA_HOME="$JAVA_HOME_DIR"
export VAXLAKE_PATHS__DATA_DIR="$DATA_DIR"
export PYSPARK_PYTHON="$VENV/bin/python"
export PYSPARK_DRIVER_PYTHON="$VENV/bin/python"
alias vaxenv='source "$VENV/bin/activate" && cd "$REPO"'
# <<< vaxlake <<<
EOF
fi

# Git hooks are NOT installed here on purpose: git runs on the Windows side only
# (ADR-0010), and a hook pointing to a Linux path would break Windows commits.

echo
echo "==> Done. Open a new Ubuntu terminal (or run: source ~/.bashrc), then:"
echo "    vaxenv"
echo "    java -version && vaxlake info && pytest && vaxlake smoke-test"
