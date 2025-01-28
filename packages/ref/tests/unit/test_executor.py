import pytest

from cmip_ref.executor import import_executor
from cmip_ref.executor.local import LocalExecutor
from cmip_ref_core.datasets import MetricDataset
from cmip_ref_core.executor import Executor
from cmip_ref_core.metrics import MetricExecutionDefinition


@pytest.fixture
def metric_definition(tmp_path) -> MetricExecutionDefinition:
    return MetricExecutionDefinition(
        output_fragment=tmp_path, key="mocked-metric-slug", metric_dataset=MetricDataset({})
    )


def test_import_executor():
    executor = import_executor("cmip_ref.executors.local.LocalExecutor")

    assert isinstance(executor, Executor)
    assert isinstance(executor, LocalExecutor)


def test_import_executor_missing():
    with pytest.raises(ImportError):
        import_executor("cmip_ref.executors.local.WrongExecutor")

    with pytest.raises(ImportError):
        import_executor("missing.executors.local.WrongExecutor")


class TestLocalExecutor:
    def test_is_executor(self):
        executor = LocalExecutor()

        assert executor.name == "local"
        assert isinstance(executor, Executor)

    def test_run_metric(self, metric_definition, mock_metric):
        executor = LocalExecutor()

        result = executor.run_metric(mock_metric, metric_definition)
        assert result.successful
        assert result.bundle_filename == metric_definition.output_fragment / "output.json"

    def test_raises_exception(self, metric_definition, mock_metric):
        executor = LocalExecutor()

        mock_metric.run = lambda definition: 1 / 0

        result = executor.run_metric(mock_metric, metric_definition)
        assert result.successful is False
        assert result.bundle_filename is None
