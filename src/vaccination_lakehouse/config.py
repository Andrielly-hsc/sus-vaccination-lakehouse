"""Validated configuration: ``conf/base.yaml`` + profile YAML + ``VAXLAKE_*`` environment variables.

Priority (highest first):

1. Keyword arguments passed to :class:`Settings` (used by tests)
2. Environment variables, e.g. ``VAXLAKE_SPARK__DRIVER_MEMORY=2g`` (``__`` separates nesting)
3. ``.env`` file in the working directory
4. ``conf/<profile>.yaml`` (profile from ``VAXLAKE_PROFILE``, default ``dev``)
5. ``conf/base.yaml``

Invalid values fail at start-up with a clear message ("fail fast"), long before any data is read.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

#: The 27 Brazilian federative units (26 states + Federal District), by IBGE region.
UF_BY_REGION: dict[str, tuple[str, ...]] = {
    "N": ("AC", "AM", "AP", "PA", "RO", "RR", "TO"),
    "NE": ("AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"),
    "SE": ("ES", "MG", "RJ", "SP"),
    "S": ("PR", "RS", "SC"),
    "CO": ("DF", "GO", "MS", "MT"),
}
UF_CODES = frozenset(uf for ufs in UF_BY_REGION.values() for uf in ufs)

_MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
_MEMORY = re.compile(r"^\d+[mg]$")


class ScopeConfig(BaseModel):
    """Which part of the national data the pipeline processes."""

    ufs: list[str] = Field(min_length=1, description="UF codes kept by the downloader.")
    start_month: str = Field(description="First vaccination month, YYYY-MM.")
    end_month: str = Field(description="Last vaccination month, YYYY-MM (inclusive).")

    @field_validator("ufs")
    @classmethod
    def _known_ufs(cls, ufs: list[str]) -> list[str]:
        normalised = [uf.strip().upper() for uf in ufs]
        unknown = sorted(set(normalised) - UF_CODES)
        if unknown:
            raise ValueError(f"unknown UF code(s): {', '.join(unknown)}")
        return sorted(set(normalised))

    @field_validator("start_month", "end_month")
    @classmethod
    def _month_format(cls, value: str) -> str:
        if not _MONTH.match(value):
            raise ValueError(f"month must be YYYY-MM, got {value!r}")
        return value

    @model_validator(mode="after")
    def _ordered(self) -> ScopeConfig:
        if self.start_month > self.end_month:  # YYYY-MM strings sort chronologically
            raise ValueError(f"start_month {self.start_month} is after end_month {self.end_month}")
        return self


class PathsConfig(BaseModel):
    """Where data lives. Everything below ``data_dir`` is git-ignored and reproducible."""

    data_dir: Path = Path("data")

    @property
    def landing_dir(self) -> Path:
        return self.data_dir / "landing"

    @property
    def lakehouse_dir(self) -> Path:
        return self.data_dir / "lakehouse"

    @property
    def checkpoints_dir(self) -> Path:
        return self.data_dir / "checkpoints"

    @property
    def metastore_dir(self) -> Path:
        return self.data_dir / "metastore"

    @property
    def tmp_dir(self) -> Path:
        """Scratch space for partial downloads (never read by the pipeline)."""
        return self.data_dir / "tmp"

    def table_path(self, physical_name: str) -> Path:
        """Delta table location for ``layer.table``, e.g. ``bronze.sipni_doses_raw``."""
        layer, _, table = physical_name.partition(".")
        if not table:
            raise ValueError(f"expected 'layer.table', got {physical_name!r}")
        return self.lakehouse_dir / layer / table

    def checkpoint_path(self, query_name: str) -> Path:
        return self.checkpoints_dir / query_name


class IngestionConfig(BaseModel):
    """Download and landing settings (F03)."""

    sipni_base_url: str = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/PNI/csv"
    sinasc_base_url: str = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINASC/csv"
    ibge_municipalities_url: str = (
        "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado"
    )
    timeout_seconds: int = Field(default=120, ge=5)
    max_retries: int = Field(default=5, ge=0)
    rows_per_file: int = Field(
        default=500_000,
        ge=1,
        description="Rows per landing CSV part; gzip is not splittable, so smaller parts let "
        "Spark read a month in parallel.",
    )
    keep_zip: bool = False
    max_files_per_trigger: int = Field(default=8, ge=1)


class SparkConfig(BaseModel):
    """SparkSession settings (see spark.py)."""

    app_name: str = "vaccination-lakehouse"
    master: str = "local[*]"
    driver_memory: str = "3g"
    shuffle_partitions: int = Field(default=8, ge=1)
    timezone: str = "America/Sao_Paulo"
    ui_enabled: bool = True
    catalog: Literal["hive", "in-memory"] = "hive"
    log_level: Literal["ERROR", "WARN", "INFO", "DEBUG"] = "WARN"
    extra_conf: dict[str, str] = Field(default_factory=dict)

    @field_validator("driver_memory")
    @classmethod
    def _memory_format(cls, value: str) -> str:
        if not _MEMORY.match(value.lower()):
            raise ValueError(f"driver_memory must look like '512m' or '3g', got {value!r}")
        return value.lower()


class PrivacyConfig(BaseModel):
    """Disclosure control for published outputs (docs/data/privacy_assessment.md, rule P6)."""

    suppression_threshold: int = Field(
        default=5,
        ge=3,
        description="Counts below this value (and coverages whose numerator or complement is "
        "below it) are suppressed in gold outputs and the dashboard.",
    )


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    json_format: bool = True


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge nested dictionaries; values in ``override`` win."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    content = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(content, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the top level")
    return content


class YamlProfileSource(PydanticBaseSettingsSource):
    """Settings source reading ``base.yaml`` deep-merged with ``<profile>.yaml``."""

    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        super().__init__(settings_cls)
        conf_dir = Path(os.environ.get("VAXLAKE_CONF_DIR", "conf"))
        profile = os.environ.get("VAXLAKE_PROFILE", "dev")
        profile_file = conf_dir / f"{profile}.yaml"
        if not profile_file.is_file():
            raise FileNotFoundError(f"profile {profile!r} not found: {profile_file}")
        self._data = _deep_merge(_read_yaml(conf_dir / "base.yaml"), _read_yaml(profile_file))
        self._data.setdefault("profile", profile)

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        return self._data.get(field_name), field_name, False

    def __call__(self) -> dict[str, Any]:
        return self._data


class Settings(BaseSettings):
    """All project settings, validated once at start-up."""

    model_config = SettingsConfigDict(
        env_prefix="VAXLAKE_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="forbid",  # a typo in a YAML key is an error, not silently ignored
    )

    profile: str = "dev"
    scope: ScopeConfig
    paths: PathsConfig = PathsConfig()
    spark: SparkConfig = SparkConfig()
    ingestion: IngestionConfig = IngestionConfig()
    privacy: PrivacyConfig = PrivacyConfig()
    logging: LoggingConfig = LoggingConfig()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, env_settings, dotenv_settings, YamlProfileSource(settings_cls))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings (loaded once)."""
    return Settings()
