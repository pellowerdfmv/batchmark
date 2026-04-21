"""Tests for batchmark.splitter."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.splitter import (
    SplitConfig,
    SplitResult,
    split_results,
    group_by_partition,
    format_split_summary,
)


def _r(size: int, returncode: int = 0, duration: float = 0.1) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


CFG = SplitConfig(
    partitions={
        "small": (1, 100),
        "medium": (101, 1000),
        "large": (1001, 9999),
    },
    default_partition="other",
)


def test_split_results_returns_one_per_input():
    results = [_r(10), _r(500), _r(2000)]
    split = split_results(results, CFG)
    assert len(split) == 3


def test_split_assigns_correct_partition():
    split = split_results([_r(10), _r(500), _r(2000)], CFG)
    assert split[0].partition == "small"
    assert split[1].partition == "medium"
    assert split[2].partition == "large"


def test_split_uses_default_for_unmatched():
    split = split_results([_r(99999)], CFG)
    assert split[0].partition == "other"


def test_split_none_default_gives_none_partition():
    cfg = SplitConfig(partitions={"small": (1, 100)}, default_partition=None)
    split = split_results([_r(9999)], cfg)
    assert split[0].partition is None


def test_split_result_success_flag():
    sr_ok = SplitResult(result=_r(10, returncode=0), partition="small")
    sr_fail = SplitResult(result=_r(10, returncode=1), partition="small")
    assert sr_ok.success is True
    assert sr_fail.success is False


def test_split_result_size_and_duration():
    sr = SplitResult(result=_r(42, duration=1.23), partition="small")
    assert sr.size == 42
    assert sr.duration == 1.23


def test_group_by_partition_keys():
    split = split_results([_r(10), _r(500), _r(2000)], CFG)
    groups = group_by_partition(split)
    assert set(groups.keys()) == {"small", "medium", "large"}


def test_group_by_partition_counts():
    results = [_r(10), _r(20), _r(500), _r(2000)]
    groups = group_by_partition(split_results(results, CFG))
    assert len(groups["small"]) == 2
    assert len(groups["medium"]) == 1
    assert len(groups["large"]) == 1


def test_format_split_summary_contains_partition_names():
    split = split_results([_r(10), _r(500)], CFG)
    groups = group_by_partition(split)
    summary = format_split_summary(groups)
    assert "small" in summary
    assert "medium" in summary


def test_format_split_summary_shows_counts():
    split = split_results([_r(10), _r(20, returncode=1)], CFG)
    groups = group_by_partition(split)
    summary = format_split_summary(groups)
    assert "2 results" in summary
    assert "1 successful" in summary


def test_format_split_summary_unmatched_label():
    cfg = SplitConfig(partitions={"small": (1, 10)}, default_partition=None)
    split = split_results([_r(9999)], cfg)
    groups = group_by_partition(split)
    summary = format_split_summary(groups)
    assert "(unmatched)" in summary
