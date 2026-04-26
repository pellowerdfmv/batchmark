"""Tests for batchmark.partitioner."""

from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.partitioner import (
    PartitionConfig,
    PartitionedResult,
    partition_results,
    format_partition_summary,
)


def _r(size: int, duration_s: float | None, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration_s,
        returncode=returncode,
        stdout="",
        stderr="",
    )


# ---------------------------------------------------------------------------
# PartitionConfig validation
# ---------------------------------------------------------------------------

def test_partition_config_invalid_label_count_raises() -> None:
    with pytest.raises(ValueError, match="len\\(labels\\)"):
        PartitionConfig(thresholds=[100.0], labels=["fast", "medium", "slow"])


def test_partition_config_valid_does_not_raise() -> None:
    cfg = PartitionConfig(thresholds=[100.0, 500.0], labels=["fast", "medium", "slow"])
    assert len(cfg.labels) == 3


# ---------------------------------------------------------------------------
# partition_results
# ---------------------------------------------------------------------------

def test_partition_results_returns_one_per_input() -> None:
    results = [_r(10, 0.05), _r(100, 0.5), _r(1000, 2.0)]
    partitioned = partition_results(results)
    assert len(partitioned) == 3


def test_partition_fast_below_first_threshold() -> None:
    cfg = PartitionConfig(thresholds=[200.0, 1000.0], labels=["fast", "medium", "slow"])
    pr = partition_results([_r(10, 0.1)], cfg)[0]  # 100 ms < 200 ms
    assert pr.partition == "fast"


def test_partition_medium_between_thresholds() -> None:
    cfg = PartitionConfig(thresholds=[200.0, 1000.0], labels=["fast", "medium", "slow"])
    pr = partition_results([_r(10, 0.5)], cfg)[0]  # 500 ms
    assert pr.partition == "medium"


def test_partition_slow_above_all_thresholds() -> None:
    cfg = PartitionConfig(thresholds=[200.0, 1000.0], labels=["fast", "medium", "slow"])
    pr = partition_results([_r(10, 2.0)], cfg)[0]  # 2000 ms
    assert pr.partition == "slow"


def test_partition_failure_gives_none_partition() -> None:
    pr = partition_results([_r(10, None, returncode=1)])[0]
    assert pr.partition is None
    assert pr.success is False


def test_partition_none_config_uses_defaults() -> None:
    pr = partition_results([_r(10, 0.05)])[0]  # 50 ms, default fast < 200
    assert pr.partition == "fast"


def test_partitioned_result_size_and_duration_proxies() -> None:
    r = _r(42, 0.123)
    pr = PartitionedResult(result=r, partition="fast")
    assert pr.size == 42
    assert pr.duration == pytest.approx(0.123)


# ---------------------------------------------------------------------------
# format_partition_summary
# ---------------------------------------------------------------------------

def test_format_partition_summary_counts_partitions() -> None:
    cfg = PartitionConfig(thresholds=[200.0, 1000.0], labels=["fast", "medium", "slow"])
    results = [_r(1, 0.05), _r(2, 0.05), _r(3, 0.5), _r(4, 2.0)]
    partitioned = partition_results(results, cfg)
    summary = format_partition_summary(partitioned)
    assert "fast=2" in summary
    assert "medium=1" in summary
    assert "slow=1" in summary


def test_format_partition_summary_includes_failed() -> None:
    results = [_r(1, None, returncode=1), _r(2, 0.05)]
    partitioned = partition_results(results)
    summary = format_partition_summary(partitioned)
    assert "failed=1" in summary


def test_format_partition_summary_empty() -> None:
    summary = format_partition_summary([])
    assert "none" in summary.lower() or summary != ""
