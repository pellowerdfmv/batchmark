"""Tests for batchmark.zipper."""

from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.zipper import (
    ZipConfig,
    ZippedPair,
    format_zip_summary,
    zip_results,
)


def _r(size: int, duration: float, ok: bool = True) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=0 if ok else 1,
        stdout="",
        stderr="",
    )


def test_zip_results_pairs_by_size_and_index():
    left = [_r(10, 0.1), _r(20, 0.2)]
    right = [_r(10, 0.15), _r(20, 0.25)]
    pairs = zip_results(left, right)
    assert len(pairs) == 2
    assert pairs[0].size == 10
    assert pairs[1].size == 20


def test_zip_results_index_increments_within_size():
    left = [_r(10, 0.1), _r(10, 0.2)]
    right = [_r(10, 0.3), _r(10, 0.4)]
    pairs = zip_results(left, right)
    assert [p.index for p in pairs] == [0, 1]


def test_zip_results_missing_right_gives_none():
    left = [_r(10, 0.1), _r(10, 0.2)]
    right = [_r(10, 0.3)]
    pairs = zip_results(left, right)
    assert len(pairs) == 2
    assert pairs[1].right is None


def test_zip_results_missing_left_gives_none():
    left = [_r(10, 0.1)]
    right = [_r(10, 0.3), _r(10, 0.4)]
    pairs = zip_results(left, right)
    assert pairs[1].left is None


def test_delta_positive_when_right_slower():
    left = [_r(10, 0.1)]
    right = [_r(10, 0.2)]
    pairs = zip_results(left, right)
    assert pairs[0].delta == pytest.approx(0.1)


def test_delta_negative_when_right_faster():
    left = [_r(10, 0.2)]
    right = [_r(10, 0.1)]
    pairs = zip_results(left, right)
    assert pairs[0].delta == pytest.approx(-0.1)


def test_delta_none_when_left_failed():
    left = [_r(10, 0.2, ok=False)]
    right = [_r(10, 0.1)]
    pairs = zip_results(left, right)
    assert pairs[0].delta is None


def test_delta_none_when_right_failed():
    left = [_r(10, 0.1)]
    right = [_r(10, 0.2, ok=False)]
    pairs = zip_results(left, right)
    assert pairs[0].delta is None


def test_both_present_true_when_both_exist():
    left = [_r(10, 0.1)]
    right = [_r(10, 0.2)]
    pairs = zip_results(left, right)
    assert pairs[0].both_present is True


def test_both_present_false_when_one_missing():
    left = [_r(10, 0.1), _r(10, 0.2)]
    right = [_r(10, 0.3)]
    pairs = zip_results(left, right)
    assert pairs[1].both_present is False


def test_format_zip_summary_counts():
    left = [_r(10, 0.1), _r(20, 0.3)]
    right = [_r(10, 0.05), _r(20, 0.4)]
    pairs = zip_results(left, right)
    cfg = ZipConfig(left_label="A", right_label="B")
    summary = format_zip_summary(pairs, cfg)
    assert "B faster: 1" in summary
    assert "B slower: 1" in summary


def test_zip_empty_inputs_returns_empty():
    assert zip_results([], []) == []
