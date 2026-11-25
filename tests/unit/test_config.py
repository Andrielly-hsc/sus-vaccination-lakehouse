"""Configuration loading, priority and validation."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from vaccination_lakehouse.config import UF_CODES, Settings, _deep_merge


def test_ci_profile_is_loaded_over_base() -> None:
    settings = Settings()

    assert settings.profile == "ci"
    assert settings.scope.ufs == ["ES"]  # from ci.yaml
    assert settings.spark.shuffle_partitions == 2  # from ci.yaml
    assert settings.spark.timezone == "America/Sao_Paulo"  # inherited from base.yaml


def test_environment_variables_override_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VAXLAKE_SPARK__DRIVER_MEMORY", "2G")
    monkeypatch.setenv("VAXLAKE_SCOPE__UFS", '["sp", "es", "SP"]')

    settings = Settings()

    assert settings.spark.driver_memory == "2g"
    assert settings.scope.ufs == ["ES", "SP"]  # normalised, deduplicated, sorted


def test_paths_are_derived_from_data_dir(tmp_path: Path) -> None:
    settings = Settings(paths={"data_dir": tmp_path})

    assert settings.paths.landing_dir == tmp_path / "landing"
    assert settings.paths.checkpoints_dir == tmp_path / "checkpoints"


@pytest.mark.parametrize(
    ("scope", "message"),
    [
        ({"ufs": ["SP", "XX"], "start_month": "2025-01", "end_month": "2025-02"}, "unknown UF"),
        ({"ufs": [], "start_month": "2025-01", "end_month": "2025-02"}, "at least 1"),
        ({"ufs": ["SP"], "start_month": "2025-13", "end_month": "2025-12"}, "YYYY-MM"),
        ({"ufs": ["SP"], "start_month": "2025-06", "end_month": "2025-01"}, "is after"),
    ],
)
def test_invalid_scope_fails_fast(scope: dict, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Settings(scope=scope)


def test_invalid_driver_memory_is_rejected() -> None:
    with pytest.raises(ValidationError, match="driver_memory"):
        Settings(spark={"driver_memory": "lots"})


def test_unknown_yaml_key_is_an_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "base.yaml").write_text(
        'scope: {ufs: [SP], start_month: "2025-01", end_month: "2025-01"}\nsparkk: {}\n',
        encoding="utf-8",
    )
    (tmp_path / "ci.yaml").write_text("{}\n", encoding="utf-8")
    monkeypatch.setenv("VAXLAKE_CONF_DIR", str(tmp_path))

    with pytest.raises(ValidationError, match="sparkk"):
        Settings()


def test_missing_profile_file_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VAXLAKE_PROFILE", "does-not-exist")

    with pytest.raises(FileNotFoundError, match="does-not-exist"):
        Settings()


def test_deep_merge_keeps_unrelated_nested_keys() -> None:
    base = {"spark": {"master": "local[*]", "driver_memory": "3g"}, "x": 1}
    override = {"spark": {"driver_memory": "1g"}}

    assert _deep_merge(base, override) == {
        "spark": {"master": "local[*]", "driver_memory": "1g"},
        "x": 1,
    }


def test_all_27_federative_units_are_known() -> None:
    assert len(UF_CODES) == 27
    assert {"SP", "MG", "RJ", "ES", "DF"} <= UF_CODES
