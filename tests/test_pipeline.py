"""Integration-style tests for batchmark.pipeline."""

from unittest.mock import call, patch

from batchmark.filter import FilterConfig
from batchmark.pipeline import PipelineConfig, run_and_filter
from batchmark.timer import TimingResult
from batchmark.warmup import WarmupConfig


def _r(size: int, success: bool = True, duration: float = 0.1) -> TimingResult:
    return TimingResult(
        command="cmd",
        size=size,
        duration=duration,
        returncode=0 if success else 1,
        stdout="",
        stderr="",
    )


@patch("batchmark.pipeline.run_batch")
@patch("batchmark.pipeline.run_warmup")
def test_run_and_filter_calls_warmup_per_size(mock_warmup, mock_batch):
    mock_batch.return_value = [_r(10), _r(20)]
    cfg = PipelineConfig(sizes=[10, 20], warmup=WarmupConfig(runs=2))
    run_and_filter("echo {size}", cfg)
    assert mock_warmup.call_count == 2


@patch("batchmark.pipeline.run_batch")
@patch("batchmark.pipeline.run_warmup")
def test_run_and_filter_skips_warmup_when_zero(mock_warmup, mock_batch):
    mock_batch.return_value = [_r(10)]
    cfg = PipelineConfig(sizes=[10], warmup=WarmupConfig(runs=0))
    run_and_filter("echo {size}", cfg)
    mock_warmup.assert_called_once()  # still called, just 0 runs inside


@patch("batchmark.pipeline.run_batch")
@patch("batchmark.pipeline.run_warmup")
def test_run_and_filter_applies_success_filter(mock_warmup, mock_batch):
    mock_batch.return_value = [_r(10, success=True), _r(20, success=False)]
    cfg = PipelineConfig(
        sizes=[10, 20], filter=FilterConfig(only_success=True)
    )
    results = run_and_filter("echo {size}", cfg)
    assert all(r.success for r in results)
    assert len(results) == 1


@patch("batchmark.pipeline.run_batch")
@patch("batchmark.pipeline.run_warmup")
def test_run_and_filter_applies_max_duration_filter(mock_warmup, mock_batch):
    mock_batch.return_value = [_r(10, duration=0.5), _r(20, duration=2.0)]
    cfg = PipelineConfig(sizes=[10, 20], filter=FilterConfig(max_duration=1.0))
    results = run_and_filter("echo {size}", cfg)
    assert len(results) == 1
    assert results[0].size == 10


@patch("batchmark.pipeline.run_batch")
@patch("batchmark.pipeline.run_warmup")
def test_run_and_filter_passes_timeout(mock_warmup, mock_batch):
    mock_batch.return_value = []
    cfg = PipelineConfig(sizes=[10], timeout=3.0)
    run_and_filter("echo {size}", cfg)
    _, kwargs = mock_batch.call_args
    assert kwargs.get("timeout") == 3.0
