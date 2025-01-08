import pathlib

import pytest
from ref_core.datasets import DatasetCollection, MetricDataset, SourceDatasetType
from ref_core.metrics import MetricExecutionDefinition
from ref_metrics_example.example import GlobalMeanTimeseries, calculate_annual_mean_timeseries


@pytest.fixture
def metric_dataset(cmip6_data_catalog) -> MetricDataset:
    selected_dataset = cmip6_data_catalog[
        cmip6_data_catalog["instance_id"] == cmip6_data_catalog.instance_id.iloc[0]
    ]
    return MetricDataset(
        {
            SourceDatasetType.CMIP6: DatasetCollection(
                selected_dataset,
                "instance_id",
            )
        }
    )


def test_annual_mean(sample_data_dir, metric_dataset):
    annual_mean = calculate_annual_mean_timeseries(metric_dataset["cmip6"].path.to_list())

    assert annual_mean.time.size == 286


def test_example_metric(tmp_path, metric_dataset, cmip6_data_catalog, mocker):
    metric = GlobalMeanTimeseries()
    ds = cmip6_data_catalog.groupby("instance_id").first()
    output_directory = tmp_path / "output"

    mock_calc = mocker.patch("ref_metrics_example.example.calculate_annual_mean_timeseries")

    mock_calc.return_value.attrs.__getitem__.return_value = "ABC"

    definition = MetricExecutionDefinition(
        output_directory=output_directory,
        output_fragment=pathlib.Path(metric.slug),
        key="global_mean_timeseries",
        metric_dataset=MetricDataset(
            {
                SourceDatasetType.CMIP6: DatasetCollection(ds, "instance_id"),
            }
        ),
    )

    result = metric.run(definition)

    assert mock_calc.call_count == 1

    assert str(result.bundle_filename) == "output.json"

    output_bundle_path = definition.output_directory / definition.output_fragment / result.bundle_filename

    assert result.successful
    assert output_bundle_path.exists()
    assert output_bundle_path.is_file()
