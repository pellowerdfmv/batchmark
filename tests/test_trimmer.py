"""Tests for batchmark.trimmer."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.trimmer import (
    TrimmerConfig,
    TrimmedResult,
    trim_results,
    format_trim_summary,
)


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_trim_results_returns_one_per_input():
    results = [_r(10), _r(10), _r(10)]
    out = trim_results(results)
    assert len(out) == 3


def test_trim_results_empty_input():
    assert trim_results([]) == []


def test_no_trim_with_default_config():
    results = [_r(10), _r(10), _r(20)]
    out = trim_results(results)
    assert all(not r.trimmed for r in out)


def test_trim_head_removes_first_n():
    results = [_r(10), _r(10), _r(10), _r(10)]
    out = trim_results(results, TrimmerConfig(head=1))
    trimmed = [r.trimmed for r in out]
    assert trimmed == [True, False, False, False]


def test_trim_tail_removes_last_n():
    results = [_r(10), _r(10), _r(10), _r(10)]
    out = trim_results(results, TrimmerConfig(tail=2))
    trimmed = [r.trimmed for r in out]
    assert trimmed == [False, False, True, True]


def test_trim_head_and_tail():
    results = [_r(10), _r(10), _r(10), _r(10), _r(10)]
    out = trim_results(results, TrimmerConfig(head=1, tail=1))
    trimmed = [r.trimmed for r in out]
    assert trimmed == [True, False, False, False, True]


def test_trim_per_size_group():
    results = [_r(10), _r(10), _r(20), _r(20)]
    out = trim_results(results, TrimmerConfig(head=1))
    trimmed_by_size: dict = {}
    for r in out:
        trimmed_by_size.setdefault(r.size, []).append(r.trimmed)
    assert trimmed_by_size[10] == [True, False]
    assert trimmed_by_size[20] == [True, False]


def test_trim_more_than_group_size_marks_all():
    results = [_r(10), _r(10)]
    out = trim_results(results, TrimmerConfig(head=5))
    assert all(r.trimmed for r in out)


def test_trimmed_result_preserves_original():
    r = _r(100, duration=0.42)
    out = trim_results([r])
    assert out[0].result is r
    assert out[0].duration == pytest.approx(0.42)


def test_negative_head_raises():
    with pytest.raises(ValueError):
        TrimmerConfig(head=-1)


def test_negative_tail_raises():
    with pytest.raises(ValueError):
        TrimmerConfig(tail=-1)


def test_format_trim_summary_counts():
    results = [_r(10), _r(10), _r(10)]
    out = trim_results(results, TrimmerConfig(head=1, tail=1))
    summary = format_trim_summary(out)
    assert "3 total" in summary
    assert "1 kept" in summary
    assert "2 trimmed" in summary
