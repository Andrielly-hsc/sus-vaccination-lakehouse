"""Fail when a contract changed in a breaking way without the required version bump.

Compares every ``contracts/<layer>/*.odcs.yaml`` in the working tree with the same file on a
base git ref (``origin/main`` in CI). Rules: vaccination_lakehouse.contracts.compat.

Usage::

    python scripts/check_contract_compat.py --base origin/main
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from vaccination_lakehouse.contracts.compat import Impact, check, diff

ROOT = Path(__file__).resolve().parents[1]
LAYERS = ("source", "bronze", "silver", "gold")


def git_show(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout if result.returncode == 0 else None


def git_ls(ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "contracts/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        p for p in result.stdout.splitlines() if p.endswith(".odcs.yaml") and "/schema/" not in p
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main", help="git ref to compare with")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # arrows and marks on any console

    current = {
        p.relative_to(ROOT).as_posix()
        for layer in LAYERS
        for p in (ROOT / "contracts" / layer).glob("*.odcs.yaml")
    }
    base_files = git_ls(args.base)
    errors: list[str] = []

    for path in sorted(base_files - current):
        errors.append(f"{path}: removed. Retire a contract with `status: retired` instead.")
    for path in sorted(current - base_files):
        print(f"new      {path}")
    for path in sorted(current & base_files):
        old = yaml.safe_load(git_show(args.base, path) or "{}")
        new = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
        changes = [c for c in diff(old, new) if c.impact is not Impact.NONE]
        problems = check(old, new)
        label = "BREAKING" if any(c.impact is Impact.BREAKING for c in changes) else "changed"
        if changes or old.get("version") != new.get("version"):
            print(f"{label:<8} {path} {old.get('version')} → {new.get('version')}")
            for change in changes:
                print(f"           - {change.message}")
        errors += [f"{path}: {problem}" for problem in problems]

    if errors:
        print("\nContract compatibility check FAILED:")
        for error in errors:
            print(f"  ✗ {error}")
        return 1
    print("\nContract compatibility check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
