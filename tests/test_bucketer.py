"""Tests for batchmark.bucketer."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.bucketer import (
    BucketConfig,
    BucketedResult,
    bucket_results,
    format_bucket_summary,
)


def _r(size: int, duration_s: float | None = None, success: bool = True) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration_s,
        returncode=0 if success else 1,
        stdout="",
        stderr="",
        success=success,
    )


CONFIG = BucketConfig(
    thresholds=[(100.0, "fast"), (500.0, "medium")],
    default_label="slow",
)


def test_bucket_results_returns_one_per_input():
    results = [_r(10, 0.05), _r(20, 0.3), _r(30, 1.0)]
    out = bucket_results(results, CONFIG)
    assert len(out) == 3


def test_bucket_fast_below_first_threshold():
    out = bucket_results([_r(10, 0.05)], CONFIG)  # 50 ms <= 100 ms
    assert out[0].bucket == "fast"


def test_bucket_medium_between_thresholds():
    out = bucket_results([_r(10, 0.2)], CONFIG)  # 200 ms <= 500 ms
    assert out[0].bucket == "medium"


def test_bucket_slow_above_all_thresholds():
    out = bucket_results([_r(10, 1.5)], CONFIG)  # 1500 ms > 500 ms
    assert out[0].bucket == "slow"


def test_bucket_failed_result_gets_none():
    out = bucket_results([_r(10, None, success=False)], CONFIG)
    assert out[0].bucket is None


def test_bucket_preserves_result_reference():
    r = _r(42, 0.01)
    out = bucket_results([r], CONFIG)
    assert out[0].result is r


def test_bucket_no_config_uses_defaults():
    """With no thresholds everything lands in default_label."""
    out = bucket_results([_r(1, 0.1), _r(2, 10.0)])
    assert all(br.bucket == "slow" for br in out)


def test_bucket_empty_input():
    assert bucket_results([], CONFIG) == []


def test_format_bucket_summary_counts_correctly():
    results = [
        _r(1, 0.05),   # fast
        _r(2, 0.05),   # fast
        _r(3, 0.3),    # medium
        _r(4, 2.0),    # slow
        _r(5, None, success=False),  # failed
    ]
    out = bucket_results(results, CONFIG)
    summary = format_bucket_summary(out)
    assert "fast=2" in summary
    assert "medium=1" in summary
    assert "slow=1" in summary
    assert "failed=1" in summary


def test_format_bucket_summary_empty():
    summary = format_bucket_summary([])
    assert "empty" in summary


def test_bucketed_result_properties_delegate_to_inner():
    r = _r(99, 0.25)
    br = BucketedResult(result=r, bucket="medium")
    assert br.size == 99
    assert br.duration == 0.25
    assert br.success is True
