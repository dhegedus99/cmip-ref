import platform
from pathlib import Path

import pandas as pd
import pytest

from cmip_ref.config import default_metric_providers
from cmip_ref.database import Database
from cmip_ref.models import MetricExecution


def create_execution_dataframe(executions):
    data = []

    for execution in executions:
        assert len(execution.results) == 1
        result = execution.results[0]

        data.append(
            {
                "metric": execution.metric.slug,
                "provider": execution.metric.provider.slug,
                "execution_id": execution.id,
                "result_id": result.id,
                "execution_key": execution.key,
                "successful": result.successful,
            }
        )

    return pd.DataFrame(data)


@pytest.fixture
def config(config, monkeypatch):
    """
    Overwrite the default test config to use the metric providers for AR7 FT
    """
    # Force the default metric providers
    config.metric_providers = default_metric_providers()

    # Put the conda environments in a shared location
    # ROOT / .ref / software
    config.paths.software = Path(__file__).parents[3] / ".ref" / "software"

    # Write the config to disk so it is used by the CLI
    config.save()

    return config


@pytest.mark.slow
def test_solve_ar7_ft(
    sample_data_dir,
    config,
    invoke_cli,
    monkeypatch,
):
    # Arm-based MacOS users will need to set the environment variable `MAMBA_PLATFORM=osx-64`
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        monkeypatch.setenv("MAMBA_PLATFORM", "osx-64")

    assert len(config.metric_providers) == 3

    db = Database.from_config(config)

    # Ingest the sample data
    invoke_cli(["datasets", "ingest", "--source-type", "cmip6", str(sample_data_dir / "CMIP6")])
    invoke_cli(["datasets", "ingest", "--source-type", "obs4mips", str(sample_data_dir / "obs4MIPs")])

    # Solve
    # This will also create conda environments for the metric providers
    invoke_cli(["--verbose", "solve", "--timeout", f"{60 * 60}"])

    executions = db.session.query(MetricExecution).all()
    df = create_execution_dataframe(executions)
    print(df)

    # Check that all 3 metric providers have been used
    assert len(df["provider"].unique()) == 3

    # Check that all metrics have been successful
    assert df["successful"].all(), df[["metric", "successful"]]
