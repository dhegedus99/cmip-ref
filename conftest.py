"""
Re-useable fixtures etc. for tests that are shared across the whole project

See https://docs.pytest.org/en/7.1.x/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
"""

import pathlib
from pathlib import Path

import esgpull
import pandas as pd
import pytest
from click.testing import Result
from ref_core.datasets import SourceDatasetType
from ref_core.metrics import DataRequirement, MetricExecutionDefinition, MetricResult
from ref_core.providers import MetricsProvider
from typer.testing import CliRunner

from ref import cli
from ref.config import Config
from ref.datasets.cmip6 import CMIP6DatasetAdapter


@pytest.fixture
def esgf_data_dir() -> Path:
    pull = esgpull.Esgpull()

    return pull.config.paths.data


@pytest.fixture
def cmip6_data_catalog(esgf_data_dir) -> pd.DataFrame:
    adapter = CMIP6DatasetAdapter()
    return adapter.find_local_datasets(esgf_data_dir)


@pytest.fixture(autouse=True)
def config(tmp_path, monkeypatch) -> Config:
    monkeypatch.setenv("REF_CONFIGURATION", str(tmp_path / "ref"))

    # Uses the default configuration
    cfg = Config.load(tmp_path / "ref" / "ref.toml")

    # Allow adding datasets from outside the tree for testing
    cfg.paths.allow_out_of_tree_datasets = True

    # Use a SQLite in-memory database for testing
    # cfg.db.database_url = "sqlite:///:memory:"
    cfg.save()

    return cfg


@pytest.fixture
def invoke_cli():
    """
    Invoke the CLI with the given arguments and verify the exit code
    """

    # We want to split stderr and stdout
    # stderr == logging
    # stdout == output from commands
    runner = CliRunner(mix_stderr=False)

    def _invoke_cli(args: list[str], expected_exit_code: int = 0) -> Result:
        result = runner.invoke(
            app=cli.app,
            args=args,
        )

        if result.exit_code != expected_exit_code:
            print(result.stdout)
            print(result.stderr)

            if result.exception:
                raise result.exception
            raise ValueError(f"Expected exit code {expected_exit_code}, got {result.exit_code}")
        return result

    return _invoke_cli


class MockMetric:
    name = "mock"
    slug = "mock"

    def __init__(self, temp_dir: pathlib.Path) -> None:
        self.temp_dir = temp_dir

    # This runs on every dataset
    data_requirements = (DataRequirement(source_type=SourceDatasetType.CMIP6, filters=(), group_by=None),)

    def run(self, definition: MetricExecutionDefinition) -> MetricResult:
        # TODO: This doesn't write output.json, use build function?
        return MetricResult(
            bundle_filename=self.temp_dir / definition.output_fragment / "output.json",
            successful=True,
            definition=definition,
        )


class FailedMetric:
    name = "failed"
    slug = "failed"

    data_requirements = (DataRequirement(source_type=SourceDatasetType.CMIP6, filters=(), group_by=None),)

    def run(self, definition: MetricExecutionDefinition) -> MetricResult:
        return MetricResult.build_from_failure(definition)


@pytest.fixture
def provider(tmp_path) -> MetricsProvider:
    provider = MetricsProvider("mock_provider", "v0.1.0")
    provider.register(MockMetric(tmp_path))
    provider.register(FailedMetric())

    return provider


@pytest.fixture
def mock_metric(tmp_path) -> MockMetric:
    return MockMetric(tmp_path)
