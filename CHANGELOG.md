# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Planning documentation: architecture, ADRs, backlog of features and tasks.
- Repository conventions: `.editorconfig`, pull request template, changelog.
- WSL2 development setup script and a dev container for GitHub Codespaces (Python 3.11, Java 17), with a setup guide.
- Packaging with `pyproject.toml`, `src/` layout and a pinned lock file (PySpark 4.1.4, delta-spark 4.4.1).
- ruff and pre-commit hooks.
- Delta-enabled SparkSession factory, validated configuration profiles (`conf/*.yaml`, `VAXLAKE_*`)
  and JSON logging with a run id; `vaxlake info` and `vaxlake smoke-test` commands.
- pytest scaffolding with a shared SparkSession fixture and coverage.
- GitHub Actions CI: lint, unit and Spark tests on Java 17, CLI smoke test.
- Source documentation measured from HTTP-Range samples of the SI-PNI files, data dictionary
  (56 columns, 35 kept), reference data (IBGE, SINASC) and the official coverage method (NT 90/2025).
- Seeds: coverage indicators with targets and schedule rules, vaccine and dose code tables.
- ODCS v3.2.0 data contracts for every source and lakehouse table, validated against the official
  JSON Schema; Spark schemas generated from them; SemVer compatibility check in CI.
- LGPD privacy assessment with measured re-identification risk and rules P1–P11; configurable
  small-cell suppression threshold.
