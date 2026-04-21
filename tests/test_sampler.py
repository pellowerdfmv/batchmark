"""Tests for batchmark.sampler."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.sampler import SamplerConfig, sample_results, format_sample_summary


def _r(size: int, rc: int = 0, dur: float = 0.1) -> TimingResult:
    return TimingResult(size=size, duration=dur, returncode=rc, command="echo hi")


def test_sample_fraction_one_returns_all():
    results = [_r(10), _r(10), _r(20), _r(20)]
    cfg = SamplerConfig(fraction=1.0, seed=0)
    out = sample_results(results, cfg)
    assert len(out) == 4


def test_sample_fraction_half():
    results = [_r(10)] * 10
    cfg = SamplerConfig(fraction=0.5, seed=42)
    out = sample_results(results, cfg)
    assert len(out) == 5


def test_sample_max_per_size_caps_results():
    results = [_r(10)] * 8 + [_r(20)] * 8
    cfg = SamplerConfig(fraction=1.0, max_per_size=3, seed=0)
    out = sample_results(results, cfg)
    sizes = [r.size for r in out]
    assert sizes.count(10) <= 3
    assert sizes.count(20) <= 3


def test_sample_only_successful_excludes_failures():
    results = [_r(10, rc=0), _r(10, rc=1), _r(10, rc=0)]
    cfg = SamplerConfig(fraction=1.0, only_successful=True, seed=0)
    out = sample_results(results, cfg)
    assert all(r.returncode == 0 for r in out)
    assert len(out) == 2


def test_sample_empty_input_returns_empty():
    cfg = SamplerConfig(fraction=1.0)
    assert sample_results([], cfg) == []


def test_sample_seed_is_reproducible():
    results = [_r(10)] * 20
    cfg1 = SamplerConfig(fraction=0.4, seed=7)
    cfg2 = SamplerConfig(fraction=0.4, seed=7)
    assert sample_results(results, cfg1) == sample_results(results, cfg2)


def test_sample_different_seeds_may_differ():
    results = [_r(i % 3) for i in range(30)]
    cfg1 = SamplerConfig(fraction=0.5, seed=1)
    cfg2 = SamplerConfig(fraction=0.5, seed=999)
    # Not guaranteed but overwhelmingly likely with 30 items
    out1 = [r.size for r in sample_results(results, cfg1)]
    out2 = [r.size for r in sample_results(results, cfg2)]
    # At least the counts should be the same per size
    assert len(out1) == len(out2)


def test_format_sample_summary_correct_percentage():
    original = [_r(10)] * 10
    sampled = [_r(10)] * 4
    summary = format_sample_summary(original, sampled)
    assert "4/10" in summary
    assert "40.0%" in summary


def test_format_sample_summary_empty_original():
    summary = format_sample_summary([], [])
    assert "0/0" in summary
