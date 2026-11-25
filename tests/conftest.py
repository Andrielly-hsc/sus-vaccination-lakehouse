"""Shared pytest fixtures.

* Tests always run with the ``ci`` profile (tiny scope, small Spark) unless a test says otherwise.
* One SparkSession per test session: starting a JVM per test would make the suite unusable.
* Tests that use the ``spark`` fixture are marked ``spark`` automatically. Without Java they are
  skipped *locally* with a visible reason, but they always fail loudly in CI.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterator

import pytest

os.environ["VAXLAKE_PROFILE"] = "ci"

from vaccination_lakehouse.config import Settings, get_settings  # noqa: E402

JAVA_AVAILABLE = bool(os.environ.get("JAVA_HOME") or shutil.which("java"))
IN_CI = os.environ.get("CI", "").lower() == "true"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    skip_no_java = pytest.mark.skip(
        reason="Java 17 not found - run Spark tests in WSL2 (see docs/setup.md)"
    )
    for item in items:
        if "spark" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.spark)
            if not JAVA_AVAILABLE and not IN_CI:
                item.add_marker(skip_no_java)


@pytest.fixture(autouse=True)
def _fresh_settings() -> Iterator[None]:
    """Settings are cached per process; clear the cache so env changes in a test take effect."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def spark_settings(tmp_path_factory: pytest.TempPathFactory) -> Settings:
    """``ci`` profile with all data paths inside a temporary folder."""
    data_dir = tmp_path_factory.mktemp("data")
    return Settings(paths={"data_dir": data_dir})


@pytest.fixture(scope="session")
def spark(spark_settings: Settings):
    """A Delta-enabled SparkSession shared by the whole test session."""
    from vaccination_lakehouse.spark import get_spark

    session = get_spark(spark_settings, app_name="vaxlake-tests")
    yield session
    session.stop()
