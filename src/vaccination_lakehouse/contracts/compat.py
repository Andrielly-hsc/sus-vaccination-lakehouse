"""Semantic-versioning rules for data contracts (contracts/README.md, "Versioning").

A change that can break a consumer (removing, renaming or retyping a column, making it required,
changing the key or the partitioning) is *breaking* and needs a major version bump. Adding an
optional column or a rule is *additive* (minor). Text-only edits need no bump.

Before 1.0.0 (``status: proposed``), SemVer allows breaking changes in minor versions, so a
breaking change to a 0.y.z contract needs at least a minor bump.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class Impact(IntEnum):
    NONE = 0
    ADDITIVE = 1
    BREAKING = 2


@dataclass(frozen=True)
class Change:
    impact: Impact
    message: str


def _objects(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {obj["name"]: obj for obj in contract.get("schema") or []}


def _props(obj: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {prop["name"]: prop for prop in obj.get("properties") or []}


def _rules(obj: dict[str, Any]) -> list[Any]:
    """Quality rules without their free-text fields (editing a description is not a change)."""
    text_fields = {"description", "businessImpact"}
    rules = [dict(rule) for rule in obj.get("quality") or []]
    for prop in obj.get("properties") or []:
        rules += [{**rule, "column": prop["name"]} for rule in prop.get("quality") or []]
    return [{k: v for k, v in rule.items() if k not in text_fields} for rule in rules]


def diff(old: dict[str, Any], new: dict[str, Any]) -> list[Change]:
    """List the changes between two versions of a contract, with their impact."""
    changes: list[Change] = []
    old_objects, new_objects = _objects(old), _objects(new)

    for name in old_objects.keys() - new_objects.keys():
        changes.append(Change(Impact.BREAKING, f"table '{name}' removed"))
    for name in new_objects.keys() - old_objects.keys():
        changes.append(Change(Impact.ADDITIVE, f"table '{name}' added"))

    for name in old_objects.keys() & new_objects.keys():
        before, after = old_objects[name], new_objects[name]
        if before.get("physicalName") != after.get("physicalName"):
            changes.append(Change(Impact.BREAKING, f"{name}: physicalName changed"))
        old_props, new_props = _props(before), _props(after)

        for col in old_props.keys() - new_props.keys():
            changes.append(Change(Impact.BREAKING, f"{name}.{col} removed (or renamed)"))
        for col in new_props.keys() - old_props.keys():
            required = new_props[col].get("required", False)
            impact = Impact.BREAKING if required else Impact.ADDITIVE
            changes.append(
                Change(impact, f"{name}.{col} added ({'required' if required else 'optional'})")
            )
        for col in old_props.keys() & new_props.keys():
            a, b = old_props[col], new_props[col]
            for key in ("logicalType", "physicalType"):
                if a.get(key) != b.get(key):
                    changes.append(
                        Change(Impact.BREAKING, f"{name}.{col} {key} {a.get(key)} → {b.get(key)}")
                    )
            if not a.get("required", False) and b.get("required", False):
                changes.append(Change(Impact.BREAKING, f"{name}.{col} became required"))
            if a.get("required", False) and not b.get("required", False):
                changes.append(Change(Impact.ADDITIVE, f"{name}.{col} became optional"))
            for key in ("primaryKey", "partitioned"):
                if bool(a.get(key)) != bool(b.get(key)):
                    changes.append(Change(Impact.BREAKING, f"{name}.{col} {key} changed"))
            if a.get("enum") != b.get("enum"):
                changes.append(Change(Impact.BREAKING, f"{name}.{col} allowed values changed"))

        old_rules, new_rules = _rules(before), _rules(after)
        if old_rules != new_rules:
            removed = [r for r in old_rules if r not in new_rules]
            added = [r for r in new_rules if r not in old_rules]
            if any(r.get("severity") == "error" for r in added):
                changes.append(
                    Change(Impact.BREAKING, f"{name}: new or tightened error-level rule")
                )
            elif added or removed:
                changes.append(Change(Impact.ADDITIVE, f"{name}: quality rules changed"))
    return changes


def _parse(version: str) -> tuple[int, int, int]:
    major, minor, patch = (int(part) for part in str(version).split("."))
    return major, minor, patch


def required_bump(old_version: str, changes: list[Change]) -> str:
    """'major', 'minor' or 'none' — the smallest bump these changes require."""
    impact = max((c.impact for c in changes), default=Impact.NONE)
    if impact is Impact.BREAKING:
        return "minor" if _parse(old_version)[0] == 0 else "major"
    if impact is Impact.ADDITIVE:
        return "minor"
    return "none"


def bump_of(old_version: str, new_version: str) -> str:
    """Kind of bump between two versions: 'major', 'minor', 'patch', 'none' or 'downgrade'."""
    old, new = _parse(old_version), _parse(new_version)
    if new < old:
        return "downgrade"
    if new[0] > old[0]:
        return "major"
    if new[1] > old[1]:
        return "minor"
    if new[2] > old[2]:
        return "patch"
    return "none"


_ORDER = {"none": 0, "patch": 0, "minor": 1, "major": 2}


def check(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    """Return error messages; empty when the version bump matches the changes."""
    changes = diff(old, new)
    needed = required_bump(old["version"], changes)
    done = bump_of(old["version"], new["version"])
    if done == "downgrade":
        return [f"version went down: {old['version']} → {new['version']}"]
    if _ORDER[done] < _ORDER[needed]:
        details = "; ".join(c.message for c in changes if c.impact is not Impact.NONE)
        return [
            f"{old['version']} → {new['version']} is a {done} bump, but the changes need "
            f"at least a {needed} bump: {details}"
        ]
    return []
