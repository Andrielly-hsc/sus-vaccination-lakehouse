"""Semantic-versioning rules: breaking changes need a major bump (minor before 1.0.0)."""

from __future__ import annotations

import copy

import pytest

from vaccination_lakehouse.contracts.compat import Impact, bump_of, check, diff, required_bump


def base_contract(version: str = "1.0.0") -> dict:
    return {
        "id": "vaxlake-silver-t",
        "version": version,
        "schema": [
            {
                "name": "t",
                "physicalName": "silver.t",
                "properties": [
                    {
                        "name": "id",
                        "logicalType": "string",
                        "physicalType": "string",
                        "required": True,
                        "primaryKey": True,
                    },
                    {"name": "amount", "logicalType": "integer", "physicalType": "int"},
                    {
                        "name": "note",
                        "logicalType": "string",
                        "physicalType": "string",
                        "description": "free text",
                    },
                ],
                "quality": [
                    {
                        "name": "unique_id",
                        "metric": "duplicateValues",
                        "mustBe": 0,
                        "severity": "error",
                        "description": "unique",
                    }
                ],
            }
        ],
    }


def changed(version: str, mutate) -> tuple[dict, dict]:
    old = base_contract()
    new = copy.deepcopy(old)
    new["version"] = version
    mutate(new["schema"][0])
    return old, new


def drop_column(obj: dict) -> None:
    obj["properties"] = [p for p in obj["properties"] if p["name"] != "amount"]


def retype_column(obj: dict) -> None:
    obj["properties"][1]["physicalType"] = "bigint"


def add_optional(obj: dict) -> None:
    obj["properties"].append({"name": "extra", "logicalType": "string", "physicalType": "string"})


def add_required(obj: dict) -> None:
    obj["properties"].append(
        {"name": "extra", "logicalType": "string", "physicalType": "string", "required": True}
    )


def make_required(obj: dict) -> None:
    obj["properties"][1]["required"] = True


def edit_description(obj: dict) -> None:
    obj["properties"][2]["description"] = "better wording"
    obj["quality"][0]["description"] = "the id is unique"


@pytest.mark.parametrize("mutation", [drop_column, retype_column, add_required, make_required])
def test_breaking_change_without_major_bump_fails(mutation) -> None:
    old, new = changed("1.1.0", mutation)

    errors = check(old, new)

    assert errors and "major" in errors[0]


@pytest.mark.parametrize("mutation", [drop_column, retype_column, add_required, make_required])
def test_breaking_change_with_major_bump_passes(mutation) -> None:
    assert check(*changed("2.0.0", mutation)) == []


def test_adding_an_optional_column_needs_a_minor_bump() -> None:
    assert check(*changed("1.0.1", add_optional))  # patch is not enough
    assert check(*changed("1.1.0", add_optional)) == []


def test_text_edits_need_no_bump() -> None:
    old, new = changed("1.0.0", edit_description)

    assert diff(old, new) == []
    assert check(old, new) == []


def test_new_error_rule_is_breaking() -> None:
    def add_rule(obj: dict) -> None:
        obj["quality"].append(
            {"name": "positive", "type": "sql", "query": "...", "mustBe": 0, "severity": "error"}
        )

    old, new = changed("1.1.0", add_rule)

    assert any(c.impact is Impact.BREAKING for c in diff(old, new))
    assert check(old, new)


def test_new_warning_rule_is_additive() -> None:
    def add_rule(obj: dict) -> None:
        obj["quality"].append(
            {"name": "w", "type": "sql", "query": "...", "mustBe": 0, "severity": "warning"}
        )

    assert check(*changed("1.1.0", add_rule)) == []


def test_before_1_0_breaking_changes_need_only_a_minor_bump() -> None:
    old = base_contract("0.1.0")
    new = copy.deepcopy(old)
    new["version"] = "0.2.0"
    drop_column(new["schema"][0])

    assert required_bump("0.1.0", diff(old, new)) == "minor"
    assert check(old, new) == []


def test_version_cannot_go_down() -> None:
    old, new = changed("0.9.0", add_optional)

    assert "went down" in check(old, new)[0]


def test_removed_table_is_breaking() -> None:
    old = base_contract()
    new = {**copy.deepcopy(old), "schema": [], "version": "1.1.0"}

    assert check(old, new)


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        ("1.2.3", "2.0.0", "major"),
        ("1.2.3", "1.3.0", "minor"),
        ("1.2.3", "1.2.4", "patch"),
        ("1.2.3", "1.2.3", "none"),
        ("1.2.3", "1.2.2", "downgrade"),
    ],
)
def test_bump_of(old: str, new: str, expected: str) -> None:
    assert bump_of(old, new) == expected
