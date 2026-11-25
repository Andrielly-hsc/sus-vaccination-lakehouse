"""Every data contract is valid ODCS and follows the project conventions."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_contracts.py"

#: Tables listed in ARCHITECTURE.md §5.2 that must have a contract (schema object name).
REQUIRED_TABLES = {
    "bronze": {"sipni_doses_raw", "ref_ibge_municipalities", "ref_sinasc_live_births"},
    "silver": {"vaccination_doses", "quarantine_doses", "late_arrivals", "dim_establishment"},
    "gold": {
        "dim_municipality",
        "dim_vaccine",
        "dim_date",
        "dim_establishment",
        "fct_doses_daily",
        "ind_coverage_yearly",
        "ind_dropout_yearly",
        "ind_timeliness_monthly",
        "rt_doses_hourly",
    },
}


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_contracts", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def test_all_contracts_are_valid(capsys: pytest.CaptureFixture) -> None:
    assert _load_validator().validate() == 0, capsys.readouterr().out


@pytest.mark.parametrize("layer", sorted(REQUIRED_TABLES))
def test_every_architecture_table_has_a_contract(layer: str) -> None:
    import yaml

    names = {
        obj["name"]
        for path in (ROOT / "contracts" / layer).glob("*.odcs.yaml")
        for obj in yaml.safe_load(path.read_text(encoding="utf-8")).get("schema", [])
    }
    assert REQUIRED_TABLES[layer] <= names, f"missing: {sorted(REQUIRED_TABLES[layer] - names)}"


def test_bronze_mirrors_the_source_columns() -> None:
    import yaml

    def columns(path: Path) -> list[str]:
        obj = yaml.safe_load(path.read_text(encoding="utf-8"))["schema"][0]
        return [p["name"] for p in obj["properties"]]

    source = columns(ROOT / "contracts" / "source" / "sipni_doses.odcs.yaml")
    bronze = columns(ROOT / "contracts" / "bronze" / "sipni_doses_raw.odcs.yaml")
    assert bronze[: len(source)] == source, "bronze must keep the source columns, in order"
    assert all(name.startswith("_") for name in bronze[len(source) :]), "extra columns are metadata"
