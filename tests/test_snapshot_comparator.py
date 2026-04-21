"""Tests for batchmark.snapshot_comparator."""

import pytest

from batchmark.aggregator import AggregatedResult
from batchmark.snapshotter import SnapshotEntry
from batchmark.snapshot_comparator import diff_against_snapshot, SnapshotDiff


def _agg(size: int, mean: float) -> AggregatedResult:
    return AggregatedResult(
        size=size, runs=3, successful=3,
        mean=mean, median=mean, stdev=0.0,
        min_duration=mean, max_duration=mean,
    )


def _snap(size: int, mean: float) -> SnapshotEntry:
    return SnapshotEntry(
        size=size, mean=mean, median=mean, stdev=0.0,
        min_duration=mean, max_duration=mean, runs=3, successful=3,
    )


def test_diff_returns_one_row_per_result():
    diffs = diff_against_snapshot([_agg(10, 100.0), _agg(20, 200.0)],
                                   [_snap(10, 90.0), _snap(20, 210.0)])
    assert len(diffs) == 2


def test_diff_sorted_by_size():
    diffs = diff_against_snapshot([_agg(20, 200.0), _agg(10, 100.0)],
                                   [_snap(20, 200.0), _snap(10, 100.0)])
    assert diffs[0].size == 10
    assert diffs[1].size == 20


def test_diff_delta_positive_when_slower():
    diffs = diff_against_snapshot([_agg(10, 120.0)], [_snap(10, 100.0)])
    assert diffs[0].delta_ms == pytest.approx(20.0)


def test_diff_delta_negative_when_faster():
    diffs = diff_against_snapshot([_agg(10, 80.0)], [_snap(10, 100.0)])
    assert diffs[0].delta_ms == pytest.approx(-20.0)


def test_diff_regression_true_when_slower():
    diffs = diff_against_snapshot([_agg(10, 150.0)], [_snap(10, 100.0)])
    assert diffs[0].regression is True


def test_diff_regression_false_when_faster():
    diffs = diff_against_snapshot([_agg(10, 80.0)], [_snap(10, 100.0)])
    assert diffs[0].regression is False


def test_diff_delta_pct_correct():
    diffs = diff_against_snapshot([_agg(10, 110.0)], [_snap(10, 100.0)])
    assert diffs[0].delta_pct == pytest.approx(10.0)


def test_diff_missing_snapshot_entry_gives_none_delta():
    diffs = diff_against_snapshot([_agg(10, 100.0)], [])
    assert diffs[0].delta_ms is None
    assert diffs[0].regression is False


def test_diff_no_regression_when_equal():
    diffs = diff_against_snapshot([_agg(10, 100.0)], [_snap(10, 100.0)])
    assert diffs[0].regression is False
    assert diffs[0].delta_ms == pytest.approx(0.0)
