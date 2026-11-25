"""Structured logging and the CLI entry point."""

from __future__ import annotations

import json
import logging

import pytest
from typer.testing import CliRunner

from vaccination_lakehouse import __version__
from vaccination_lakehouse.cli import app
from vaccination_lakehouse.logging_setup import RUN_ID, JsonFormatter

runner = CliRunner()


def test_json_formatter_includes_run_id_and_extra_fields() -> None:
    record = logging.makeLogRecord(
        {"name": "vaxlake.test", "levelname": "INFO", "msg": "loaded %s files", "args": (3,)}
    )
    record.rows = 42  # what logger.info(..., extra={"rows": 42}) does

    payload = json.loads(JsonFormatter().format(record))

    assert payload["msg"] == "loaded 3 files"
    assert payload["run_id"] == RUN_ID
    assert payload["rows"] == 42
    assert payload["level"] == "INFO"


def test_version_option() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_info_shows_profile_and_scope() -> None:
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert "pyspark" in result.output
    assert "ci" in result.output
    assert "ES 2025-01..2025-01" in result.output


def test_invalid_configuration_exits_with_code_2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VAXLAKE_SCOPE__UFS", '["XX"]')

    result = runner.invoke(app, ["info"])

    assert result.exit_code == 2
    assert "unknown UF" in result.output


@pytest.mark.parametrize("json_format", [True, False])
def test_configure_logging_writes_run_id(json_format: bool, capsys: pytest.CaptureFixture) -> None:
    from vaccination_lakehouse.logging_setup import configure_logging

    configure_logging("INFO", json_format=json_format)
    logging.getLogger("vaxlake.test").info("hello")

    line = capsys.readouterr().err.strip()
    assert RUN_ID in line
    if json_format:
        assert json.loads(line)["msg"] == "hello"
    assert logging.getLogger("py4j").level == logging.WARNING
