"""Command-line interface: ``vaxlake <command>``.

Each pipeline step becomes a sub-command as features are implemented (see docs/README.md).
"""

from __future__ import annotations

import typer

from vaccination_lakehouse import __version__

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
    """Show the installed versions of the main components."""
    from importlib.metadata import version as pkg_version

    for package in ("vaccination-lakehouse", "pyspark", "delta-spark"):
        typer.echo(f"{package:<22} {pkg_version(package)}")
