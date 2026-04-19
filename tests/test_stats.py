"""Tests for batchmark.stats aggregation utilities."""

import math
import pytest

from batchmark.timer import TimingResult
from batchmark.stats import mean, median, stdev, min_duration, max_duration, summarise


def _r(duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(command="echo hi", size=10, duration=duration,
                        returncode=returncode, stdout="", stderr="")


OK = [_r(1.0), _r(3.0), _r(2.0)]
SINGLE = [_r(5.0)]
FAILED = [_r(1.0, returncode=1), _r(2.0, returncode=-1)]
MIXED = [_r(4.0), _r(2.0), _r(1.0, returncode=1)]


def test_mean_basic():
    assert mean(OK) == pytest.approx(2.0)


def test_mean_empty_or_all_failed():
    assert math.isnan(mean(FAILED))
    assert math.isnan(mean([]))


def test_mean_ignores_failures():
    assert mean(MIXED) == pytest.approx(3.0)


def test_median_odd():
    assert median(OK) == pytest.approx(2.0)


def test_median_even():
    assert median([_r(1.0), _r(3.0)]) == pytest.approx(2.0)


def test_median_single():
    assert median(SINGLE) == pytest.approx(5.0)


def test_median_nan_when_no_success():
    assert math.isnan(median(FAILED))


def test_stdev_basic():
    result = stdev([_r(2.0), _r(4.0)])
    assert result == pytest.approx(math.sqrt(2.0))


def test_stdev_single_is_nan():
    assert math.isnan(stdev(SINGLE))


def test_min_max():
    assert min_duration(OK) == pytest.approx(1.0)
    assert max_duration(OK) == pytest.approx(3.0)


def test_min_max_nan_when_empty():
    assert math.isnan(min_duration([]))
    assert math.isnan(max_duration([]))


def test_summarise_keys():
    s = summarise(OK)
    assert set(s.keys()) == {"count", "success", "mean", "median", "stdev", "min", "max"}


def test_summarise_counts():
    s = summarise(MIXED)
    assert s["count"] == 3
    assert s["success"] == 2
