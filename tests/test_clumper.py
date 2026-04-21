"""Tests for batchmark.clumper."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.clumper import ClumperConfig, ClumpResult, clump_results, format_clump_summary


def _r(size: int, duration_ms: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration_ms=duration_ms, returncode=returncode, stdout="", stderr="")


def test_clump_results_empty_input():
    assert clump_results([]) == []


def test_clump_results_single_clump():
    results = [_r(i, float(i * 10)) for i in range(1, 4)]
    clumps = clump_results(results, ClumperConfig(clump_size=5))
    assert len(clumps) == 1
    assert clumps[0].clump_index == 0
    assert clumps[0].total_count == 3


def test_clump_results_multiple_clumps():
    results = [_r(i, float(i)) for i in range(1, 11)]
    clumps = clump_results(results, ClumperConfig(clump_size=3))
    assert len(clumps) == 4  # ceil(10/3)


def test_clump_indices_are_sequential():
    results = [_r(i, float(i)) for i in range(1, 7)]
    clumps = clump_results(results, ClumperConfig(clump_size=2))
    assert [c.clump_index for c in clumps] == [0, 1, 2]


def test_clump_sizes_field_correct():
    results = [_r(10, 1.0), _r(20, 2.0), _r(30, 3.0)]
    clumps = clump_results(results, ClumperConfig(clump_size=2))
    assert clumps[0].sizes == [10, 20]
    assert clumps[1].sizes == [30]


def test_clump_mean_correct():
    results = [_r(1, 10.0), _r(2, 20.0), _r(3, 30.0)]
    clumps = clump_results(results, ClumperConfig(clump_size=3))
    assert clumps[0].mean_ms == 20.0


def test_clump_min_max_correct():
    results = [_r(1, 5.0), _r(2, 15.0), _r(3, 10.0)]
    clumps = clump_results(results, ClumperConfig(clump_size=3))
    assert clumps[0].min_ms == 5.0
    assert clumps[0].max_ms == 15.0


def test_clump_ignores_failures_in_stats():
    results = [_r(1, 100.0, returncode=1), _r(2, 20.0), _r(3, 40.0)]
    clumps = clump_results(results, ClumperConfig(clump_size=3))
    assert clumps[0].success_count == 2
    assert clumps[0].mean_ms == 30.0


def test_clump_all_failed_gives_none_stats():
    results = [_r(1, 10.0, returncode=1), _r(2, 20.0, returncode=2)]
    clumps = clump_results(results, ClumperConfig(clump_size=5))
    assert clumps[0].mean_ms is None
    assert clumps[0].min_ms is None
    assert clumps[0].max_ms is None


def test_clump_default_config():
    results = [_r(i, float(i)) for i in range(1, 12)]
    clumps = clump_results(results)  # default clump_size=5
    assert len(clumps) == 3


def test_format_clump_summary_contains_header():
    results = [_r(1, 10.0), _r(2, 20.0)]
    clumps = clump_results(results, ClumperConfig(clump_size=5))
    summary = format_clump_summary(clumps)
    assert "Clump" in summary
    assert "Mean ms" in summary


def test_format_clump_summary_contains_values():
    results = [_r(1, 100.0), _r(2, 200.0)]
    clumps = clump_results(results, ClumperConfig(clump_size=5))
    summary = format_clump_summary(clumps)
    assert "150.00" in summary
