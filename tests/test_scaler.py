"""Tests for batchmark.scaler."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.scaler import (
    ScalerConfig,
    ScaledResult,
    scale_results,
    format_scale_summary,
)


def _r(size: int, duration: float, rc: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=rc, stdout="", stderr="")


def test_scale_results_returns_one_per_input():
    results = [_r(10, 0.1), _r(20, 0.2)]
    scaled = scale_results(results, ScalerConfig())
    assert len(scaled) == 2


def test_scale_results_identity_when_no_config():
    results = [_r(10, 0.5)]
    scaled = scale_results(results, ScalerConfig())
    assert scaled[0].scale_factor == 1.0
    assert abs(scaled[0].scaled_duration - 0.5) < 1e-9


def test_scale_results_fixed_factor():
    results = [_r(10, 0.4)]
    scaled = scale_results(results, ScalerConfig(factor=2.5))
    assert abs(scaled[0].scaled_duration - 1.0) < 1e-9


def test_scale_results_reference_size():
    # mean of size=10 is 0.5; factor = 1/0.5 = 2.0
    results = [_r(10, 0.4), _r(10, 0.6), _r(20, 1.0)]
    scaled = scale_results(results, ScalerConfig(reference_size=10))
    assert abs(scaled[0].scale_factor - 2.0) < 1e-6
    assert abs(scaled[2].scaled_duration - 2.0) < 1e-6


def test_scale_results_failed_result_has_none_scaled_duration():
    results = [_r(10, 0.1, rc=1)]
    scaled = scale_results(results, ScalerConfig(factor=3.0))
    assert scaled[0].scaled_duration is None


def test_scale_results_failed_result_not_success():
    results = [_r(10, 0.1, rc=1)]
    scaled = scale_results(results, ScalerConfig())
    assert not scaled[0].success


def test_scale_results_reference_size_no_matching_results_defaults_to_one():
    results = [_r(10, 0.5)]
    scaled = scale_results(results, ScalerConfig(reference_size=99))
    assert scaled[0].scale_factor == 1.0


def test_scale_results_reference_size_all_failed_defaults_to_one():
    results = [_r(10, 0.5, rc=1)]
    scaled = scale_results(results, ScalerConfig(reference_size=10))
    assert scaled[0].scale_factor == 1.0


def test_format_scale_summary_shows_factor():
    results = [_r(10, 0.2), _r(20, 0.4)]
    scaled = scale_results(results, ScalerConfig(factor=5.0))
    summary = format_scale_summary(scaled)
    assert "5.0000" in summary


def test_format_scale_summary_empty():
    summary = format_scale_summary([])
    assert "No results" in summary


def test_scaled_result_size_and_duration_delegates():
    r = _r(42, 0.77)
    sr = ScaledResult(result=r, scale_factor=1.0, scaled_duration=0.77)
    assert sr.size == 42
    assert abs(sr.duration - 0.77) < 1e-9
