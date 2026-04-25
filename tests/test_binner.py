"""Tests for batchmark.binner."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.binner import BinConfig, bin_results, summarize_bins


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


_CFG = BinConfig(edges=[100, 500, 1000], labels=["small", "medium", "large"])


def test_bin_results_returns_one_per_input():
    results = [_r(50), _r(200), _r(800)]
    binned = bin_results(results, _CFG)
    assert len(binned) == 3


def test_bin_small_below_first_edge():
    binned = bin_results([_r(50)], _CFG)
    assert binned[0].bin_label == "small"


def test_bin_medium_between_edges():
    binned = bin_results([_r(300)], _CFG)
    assert binned[0].bin_label == "medium"


def test_bin_large_at_upper_edge():
    binned = bin_results([_r(1000)], _CFG)
    assert binned[0].bin_label == "large"


def test_bin_overflow_above_all_edges():
    binned = bin_results([_r(2000)], _CFG)
    assert binned[0].bin_label == "overflow"


def test_bin_custom_default_label():
    cfg = BinConfig(edges=[100], labels=["tiny"], default_label="huge")
    binned = bin_results([_r(999)], cfg)
    assert binned[0].bin_label == "huge"


def test_bin_auto_label_when_no_labels_provided():
    cfg = BinConfig(edges=[100, 500])
    binned = bin_results([_r(50), _r(300)], cfg)
    assert binned[0].bin_label == "<=100"
    assert binned[1].bin_label == "<=500"


def test_bin_preserves_result_reference():
    r = _r(50)
    binned = bin_results([r], _CFG)
    assert binned[0].result is r


def test_summarize_bins_count():
    results = [_r(50), _r(60), _r(300)]
    binned = bin_results(results, _CFG)
    summaries = summarize_bins(binned)
    labels = {s.label: s.count for s in summaries}
    assert labels["small"] == 2
    assert labels["medium"] == 1


def test_summarize_bins_mean_ms():
    results = [_r(50, duration=0.2), _r(60, duration=0.4)]
    binned = bin_results(results, _CFG)
    summaries = summarize_bins(binned)
    small = next(s for s in summaries if s.label == "small")
    assert abs(small.mean_ms - 300.0) < 0.01  # (200+400)/2


def test_summarize_bins_failed_excluded_from_mean():
    results = [_r(50, duration=0.2, returncode=0), _r(60, duration=9.9, returncode=1)]
    binned = bin_results(results, _CFG)
    summaries = summarize_bins(binned)
    small = next(s for s in summaries if s.label == "small")
    assert small.successful == 1
    assert abs(small.mean_ms - 200.0) < 0.01


def test_summarize_bins_all_failed_mean_is_none():
    results = [_r(50, returncode=1)]
    binned = bin_results(results, _CFG)
    summaries = summarize_bins(binned)
    assert summaries[0].mean_ms is None


def test_summarize_bins_order_matches_first_appearance():
    results = [_r(300), _r(50), _r(800)]
    binned = bin_results(results, _CFG)
    summaries = summarize_bins(binned)
    assert [s.label for s in summaries] == ["medium", "small", "large"]
