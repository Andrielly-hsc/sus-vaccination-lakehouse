"""Command-line interface: ``vaxlake <command>``.

Each pipeline step becomes a sub-command as features are implemented (see docs/README.md).
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import typer
from pydantic import ValidationError

from vaccination_lakehouse import __version__
from vaccination_lakehouse.config import Settings, get_settings
from vaccination_lakehouse.logging_setup import configure_logging

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="vaxlake",
    help="Real-time SUS vaccination lakehouse (PySpark + Delta Lake).",
    no_args_is_help=True,
    add_completion=False,
)


def _print_version(value: bool) -> None:
    if value:
        typer.echo(f"vaxlake {__version__}")
        raise typer.Exit()


def _load_settings() -> Settings:
    """Load settings or exit with a readable message instead of a traceback."""
    try:
        return get_settings()
    except (ValidationError, FileNotFoundError, ValueError) as exc:
        typer.secho(f"Invalid configuration:\n{exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the version and exit.",
        callback=_print_version,
        is_eager=True,
    ),
) -> None:
    """Real-time SUS vaccination lakehouse (PySpark + Delta Lake)."""


@app.command()
def info() -> None:
    """Show installed versions and the active configuration profile."""
    from importlib.metadata import version as pkg_version

    settings = _load_settings()
    for package in ("vaccination-lakehouse", "pyspark", "delta-spark"):
        typer.echo(f"{package:<22} {pkg_version(package)}")
    typer.echo(f"{'profile':<22} {settings.profile}")
    typer.echo(
        f"{'scope':<22} {','.join(settings.scope.ufs)} "
        f"{settings.scope.start_month}..{settings.scope.end_month}"
    )


@app.command("smoke-test")
def smoke_test() -> None:
    """Start Spark, write and read back a small Delta table (checks Java, Spark and Delta)."""
    settings = _load_settings()
    configure_logging(settings.logging.level, settings.logging.json_format)

    from vaccination_lakehouse.spark import get_spark  # imported late: starting Spark is slow

    spark = get_spark(settings, app_name="vaxlake-smoke-test")
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "smoke_delta")
        spark.range(5).write.format("delta").save(path)
        rows = spark.read.format("delta").load(path).count()
        version = spark.sql(f"DESCRIBE HISTORY delta.`{path}`").first()["version"]
    spark.stop()

    if rows != 5:
        typer.secho(f"Expected 5 rows, read {rows}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    typer.secho(
        f"OK - Spark {spark.version} wrote and read a Delta table (version {version}).",
        fg=typer.colors.GREEN,
    )
