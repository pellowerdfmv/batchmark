"""Integration: notify_all -> print_notification_report pipeline."""

from batchmark.timer import TimingResult
from batchmark.notifier import NotifyConfig, notify_all
from batchmark.notifier_reporter import print_notification_report


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, output="")


def test_full_pipeline_no_alerts(capsys):
    results = [_r(10, 0.05), _r(100, 0.08)]
    cfg = NotifyConfig(warn_above_ms=500.0, fail_above_ms=1000.0)
    notes = notify_all(results, cfg)
    print_notification_report(notes)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_full_pipeline_with_warn(capsys):
    results = [_r(10, 0.6), _r(100, 0.05)]
    cfg = NotifyConfig(warn_above_ms=500.0)
    notes = notify_all(results, cfg)
    assert len(notes) == 1
    print_notification_report(notes)
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "size=10" in captured.out


def test_full_pipeline_with_failure_alert(capsys):
    results = [_r(10, 0.1), _r(10, 0.1, returncode=1)]
    cfg = NotifyConfig(on_any_failure=True)
    notes = notify_all(results, cfg)
    print_notification_report(notes)
    captured = capsys.readouterr()
    assert "FAIL" in captured.out


def test_full_pipeline_multiple_sizes(capsys):
    results = [
        _r(10, 0.8),   # 800 ms -> warn
        _r(100, 1.5),  # 1500 ms -> fail
    ]
    cfg = NotifyConfig(warn_above_ms=500.0, fail_above_ms=1000.0)
    notes = notify_all(results, cfg)
    assert len(notes) == 2
    levels = {n.level for n in notes}
    assert "warn" in levels
    assert "fail" in levels
