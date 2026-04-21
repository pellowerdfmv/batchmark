"""Tests for batchmark.normalizer."""

import pytest
from batchmark.timer import TimingResult
from batchmark.normalizer import (
    NormalizerConfig,
    NormalizedResult,
    normalize_results,
    format_normalized_summary,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_normalize_results_returns_one_per_input():
    results = [_r(10, 1.0), _r(10, 2.0), _r(10, 3.0)]
    out = normalize_results(results)
    assert len(out) == 3


def test_normalize_min_is_zero():
    results = [_r(10, 1.0), _r(10, 2.0), _r(10, 3.0)]
    out = normalize_results(results)
    norms = [n.normalized for n in out]
    assert min(norms) == pytest.approx(0.0)


def test_normalize_max_is_one():
    results = [_r(10, 1.0), _r(10, 2.0), _r(10, 3.0)]
    out = normalize_results(results)
    norms = [n.normalized for n in out]
    assert max(norms) == pytest.approx(1.0)


def test_normalize_middle_value():
    results = [_r(10, 0.0), _r(10, 5.0), _r(10, 10.0)]
    out = normalize_results(results)
    mid = out[1].normalized
    assert mid == pytest.approx(0.5)


def test_normalize_single_value_per_size_gives_none():
    results = [_r(10, 1.0)]
    out = normalize_results(results)
    assert out[0].normalized is None


def test_normalize_all_same_duration_gives_none():
    results = [_r(10, 2.0), _r(10, 2.0)]
    out = normalize_results(results)
    assert all(n.normalized is None for n in out)


def test_normalize_failure_excluded_by_default():
    results = [_r(10, 1.0), _r(10, 3.0), _r(10, 99.0, returncode=1)]
    out = normalize_results(results)
    # min=1.0, max=3.0 from successful only
    assert out[0].normalized == pytest.approx(0.0)
    assert out[1].normalized == pytest.approx(1.0)
    # failed result still gets a score computed against successful bounds
    assert out[2].normalized is not None


def test_normalize_failure_included_when_config_disabled():
    config = NormalizerConfig(only_successful=False)
    results = [_r(10, 1.0), _r(10, 5.0, returncode=1)]
    out = normalize_results(results, config=config)
    assert out[0].normalized == pytest.approx(0.0)
    assert out[1].normalized == pytest.approx(1.0)


def test_normalize_groups_by_size_independently():
    results = [_r(10, 1.0), _r(10, 3.0), _r(20, 100.0), _r(20, 200.0)]
    out = normalize_results(results)
    size10 = [n for n in out if n.size == 10]
    size20 = [n for n in out if n.size == 20]
    assert size10[0].normalized == pytest.approx(0.0)
    assert size10[1].normalized == pytest.approx(1.0)
    assert size20[0].normalized == pytest.approx(0.0)
    assert size20[1].normalized == pytest.approx(1.0)


def test_format_normalized_summary_counts():
    results = [_r(10, 1.0), _r(10, 2.0), _r(20, 5.0)]
    out = normalize_results(results)
    summary = format_normalized_summary(out)
    assert "2" in summary  # 2 sizes
    assert "3" in summary  # 3 total results
