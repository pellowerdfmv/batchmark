"""Tests for batchmark.retrier."""

from unittest.mock import patch, call
from batchmark.timer import TimingResult
from batchmark.retrier import RetryConfig, RetriedResult, run_with_retry


def _result(rc: int, duration: float = 0.1) -> TimingResult:
    return TimingResult(returncode=rc, duration=duration, stdout="", stderr="")


def _patched(results):
    return patch("batchmark.retrier.time_command", side_effect=results)


def test_success_on_first_attempt():
    with _patched([_result(0)]) as m:
        r = run_with_retry(["echo", "hi"])
    assert r.attempts == 1
    assert r.success is True


def test_retries_on_failure():
    with _patched([_result(1), _result(1), _result(0)]) as m:
        r = run_with_retry(["cmd"], RetryConfig(max_attempts=3, retry_on_failure=True))
    assert r.attempts == 3
    assert r.success is True


def test_stops_after_max_attempts():
    with _patched([_result(1), _result(1), _result(1)]) as m:
        r = run_with_retry(["cmd"], RetryConfig(max_attempts=3, retry_on_failure=True))
    assert r.attempts == 3
    assert r.success is False


def test_no_retry_on_failure_when_disabled():
    with _patched([_result(1)]) as m:
        r = run_with_retry(["cmd"], RetryConfig(max_attempts=3, retry_on_failure=False))
    assert r.attempts == 1


def test_retry_on_timeout_when_enabled():
    with _patched([_result(-1), _result(0)]) as m:
        r = run_with_retry(["cmd"], RetryConfig(max_attempts=3, retry_on_timeout=True))
    assert r.attempts == 2
    assert r.success is True


def test_no_retry_on_timeout_when_disabled():
    with _patched([_result(-1)]) as m:
        r = run_with_retry(["cmd"], RetryConfig(max_attempts=3, retry_on_timeout=False))
    assert r.attempts == 1


def test_all_results_recorded():
    with _patched([_result(1), _result(1), _result(0)]):
        r = run_with_retry(["cmd"], RetryConfig(max_attempts=3))
    assert len(r.all_results) == 3


def test_default_config_no_retry_on_timeout():
    cfg = RetryConfig()
    assert cfg.retry_on_timeout is False
    assert cfg.retry_on_failure is True
    assert cfg.max_attempts == 3
