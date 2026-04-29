"""Tests for batchmark.shuffler."""

from __future__ import annotations

from batchmark.shuffler import (
    ShufflerConfig,
    ShuffledResult,
    shuffle_results,
    format_shuffle_summary,
)
from batchmark.timer import TimingResult


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_shuffle_results_returns_one_per_input():
    results = [_r(1), _r(2), _r(3)]
    shuffled = shuffle_results(results, ShufflerConfig(seed=42))
    assert len(shuffled) == 3


def test_shuffle_results_empty_input():
    assert shuffle_results([]) == []


def test_shuffle_results_contains_all_original_results():
    results = [_r(1), _r(2), _r(4)]
    shuffled = shuffle_results(results, ShufflerConfig(seed=0))
    sizes = {s.result.size for s in shuffled}
    assert sizes == {1, 2, 4}


def test_shuffle_results_records_original_index():
    results = [_r(10), _r(20), _r(30)]
    shuffled = shuffle_results(results, ShufflerConfig(seed=99))
    original_indices = {s.original_index for s in shuffled}
    assert original_indices == {0, 1, 2}


def test_shuffle_results_records_shuffled_index():
    results = [_r(1), _r(2), _r(3)]
    shuffled = shuffle_results(results, ShufflerConfig(seed=7))
    assert [s.shuffled_index for s in shuffled] == list(range(len(results)))


def test_shuffle_deterministic_with_same_seed():
    results = [_r(i) for i in range(10)]
    a = shuffle_results(results, ShufflerConfig(seed=123))
    b = shuffle_results(results, ShufflerConfig(seed=123))
    assert [s.result.size for s in a] == [s.result.size for s in b]


def test_shuffle_different_seeds_may_differ():
    results = [_r(i) for i in range(10)]
    a = shuffle_results(results, ShufflerConfig(seed=1))
    b = shuffle_results(results, ShufflerConfig(seed=2))
    # With 10 elements it is astronomically unlikely both seeds produce same order
    assert [s.result.size for s in a] != [s.result.size for s in b]


def test_shuffle_per_size_keeps_sizes_grouped():
    results = [_r(1), _r(2), _r(1), _r(2), _r(1)]
    shuffled = shuffle_results(results, ShufflerConfig(seed=5, per_size=True))
    sizes = [s.result.size for s in shuffled]
    # All size-1 entries appear before size-2 entries
    first_two = sizes.index(2)
    assert all(s == 1 for s in sizes[:first_two])
    assert all(s == 2 for s in sizes[first_two:])


def test_shuffled_result_success_flag():
    ok = _r(1, returncode=0)
    fail = _r(2, returncode=1)
    shuffled = shuffle_results([ok, fail], ShufflerConfig(seed=0))
    by_size = {s.result.size: s for s in shuffled}
    assert by_size[1].success is True
    assert by_size[2].success is False


def test_format_shuffle_summary_counts():
    results = [_r(i) for i in range(5)]
    shuffled = shuffle_results(results, ShufflerConfig(seed=42))
    summary = format_shuffle_summary(shuffled)
    assert "5" in summary
