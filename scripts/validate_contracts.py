"""Validate every data contract in ``contracts/`` against the ODCS JSON Schema.

Also checks the project conventions that the standard cannot express (see contracts/README.md):
file naming, unique ids, SemVer versions and one primary key per table.

Usage::

    python scripts/validate_contracts.py            # exit code 1 if any contract is invalid
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft201909Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
SCHEMA = CONTRACTS / "schema" / "odcs-json-schema-v3.2.0.json"
LAYERS = ("source", "bronze", "silver", "gold")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def contract_files() -> list[Path]:
    return sorted(p for layer in LAYERS for p in (CONTRACTS / layer).glob("*.odcs.yaml"))


def convention_errors(path: Path, contract: dict) -> list[str]:
    errors = []
    layer = path.parent.name
    if not SEMVER.match(str(contract.get("version", ""))):
        errors.append("version must be SemVer MAJOR.MINOR.PATCH")
    if not str(contract.get("id", "")).startswith(f"vaxlake-{layer}-"):
        errors.append(f"id must start with 'vaxlake-{layer}-'")
    layer_property = next(
        (p["value"] for p in contract.get("customProperties", []) if p["property"] == "layer"), None
    )
    if layer_property != layer:
        errors.append(f"customProperties.layer must be '{layer}' (folder name)")
    for obj in contract.get("schema", []):
        keys = [p["name"] for p in obj.get("properties", []) if p.get("primaryKey")]
        if layer in ("silver", "gold") and not keys:
            errors.append(f"schema object '{obj['name']}' has no primaryKey property")
        names = [p["name"] for p in obj.get("properties", [])]
        duplicates = sorted({n for n in names if names.count(n) > 1})
        if duplicates:
            errors.append(f"schema object '{obj['name']}' repeats properties {duplicates}")
    return errors


def validate() -> int:
    validator = Draft201909Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    files = contract_files()
    seen_ids: dict[str, Path] = {}
    failures = 0
    for path in files:
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        errors = [
            f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in validator.iter_errors(contract)
        ]
        errors += convention_errors(path, contract)
        if contract.get("id") in seen_ids:
            errors.append(f"id already used by {seen_ids[contract['id']].name}")
        seen_ids[contract.get("id")] = path
        status = "OK " if not errors else "ERR"
        print(f"{status} {path.relative_to(ROOT).as_posix()} (v{contract.get('version')})")
        for error in errors:
            print(f"    - {error}")
        failures += bool(errors)
    print(f"\n{len(files) - failures}/{len(files)} contracts valid")
    return 1 if failures or not files else 0


if __name__ == "__main__":
    sys.exit(validate())
