"""Tests for batchmark.segmenter."""

from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.segmenter import (
    SegmentConfig,
    SegmentedResult,
    segment_results,
    format_segment_summary,
)


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


_CONFIG = SegmentConfig(
    thresholds=[(100, "small"), (1000, "medium")],
    default_label="large",
)


def test_segment_results_returns_one_per_input():
    results = [_r(10), _r(500), _r(2000)]
    out = segment_results(results, _CONFIG)
    assert len(out) == 3


def test_segment_small_below_first_threshold():
    out = segment_results([_r(50)], _CONFIG)
    assert out[0].segment == "small"


def test_segment_medium_between_thresholds():
    out = segment_results([_r(500)], _CONFIG)
    assert out[0].segment == "medium"


def test_segment_large_above_all_thresholds():
    out = segment_results([_r(5000)], _CONFIG)
    assert out[0].segment == "large"


def test_segment_boundary_is_exclusive_upper():
    # size == 100 should NOT fall into "small" (bound is exclusive)
    out = segment_results([_r(100)], _CONFIG)
    assert out[0].segment == "medium"


def test_segment_no_config_uses_default_label():
    out = segment_results([_r(42)])
    assert out[0].segment == "other"


def test_segment_empty_input():
    out = segment_results([], _CONFIG)
    assert out == []


def test_segmented_result_proxies_size_and_duration():
    r = _r(128, duration=0.25)
    sr = segment_results([r], _CONFIG)[0]
    assert sr.size == 128
    assert sr.duration == pytest.approx(0.25)


def test_segmented_result_success_flag():
    ok = segment_results([_r(10, returncode=0)], _CONFIG)[0]
    fail = segment_results([_r(10, returncode=1)], _CONFIG)[0]
    assert ok.success is True
    assert fail.success is False


def test_format_segment_summary_counts_correctly():
    results = [_r(10), _r(20), _r(500), _r(2000)]
    segmented = segment_results(results, _CONFIG)
    summary = format_segment_summary(segmented)
    assert "small: 2" in summary
    assert "medium: 1" in summary
    assert "large: 1" in summary


def test_format_segment_summary_empty():
    summary = format_segment_summary([])
    assert "No results" in summary
