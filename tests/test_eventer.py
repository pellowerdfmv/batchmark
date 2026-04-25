"""Tests for batchmark.eventer and batchmark.eventer_reporter."""
import pytest
from batchmark.timer import TimingResult
from batchmark.eventer import (
    EventConfig,
    EventLog,
    fire_run_start,
    fire_run_end,
    fire_batch_start,
    fire_batch_end,
    format_event_log,
)
from batchmark.eventer_reporter import format_event_summary


def _result(rc: int = 0, duration: float = 0.5) -> TimingResult:
    return TimingResult(
        size=10, command="echo hi", duration=duration,
        returncode=rc, stdout="", stderr=""
    )


def test_fire_run_start_adds_log_entry():
    log = EventLog()
    fire_run_start(EventConfig(), log, 100, "echo hi")
    assert len(log.entries) == 1
    assert "run_start" in log.entries[0]
    assert "size=100" in log.entries[0]


def test_fire_run_end_ok_logs_ok_status():
    log = EventLog()
    fire_run_end(EventConfig(), log, 100, _result(rc=0))
    assert "status=ok" in log.entries[0]


def test_fire_run_end_fail_logs_fail_status():
    log = EventLog()
    fire_run_end(EventConfig(), log, 100, _result(rc=1))
    assert "status=fail" in log.entries[0]


def test_fire_batch_start_logs_sizes():
    log = EventLog()
    fire_batch_start(EventConfig(), log, [10, 20, 30])
    assert "batch_start" in log.entries[0]
    assert "[10, 20, 30]" in log.entries[0]


def test_fire_batch_end_logs_count():
    log = EventLog()
    results = [_result(), _result()]
    fire_batch_end(EventConfig(), log, results)
    assert "count=2" in log.entries[0]


def test_callbacks_are_invoked():
    called = []
    cfg = EventConfig(
        on_run_start=lambda size, cmd: called.append(("start", size)),
        on_run_end=lambda size, res: called.append(("end", size)),
    )
    log = EventLog()
    fire_run_start(cfg, log, 42, "ls")
    fire_run_end(cfg, log, 42, _result())
    assert ("start", 42) in called
    assert ("end", 42) in called


def test_format_event_log_empty():
    log = EventLog()
    assert format_event_log(log) == "(no events)"


def test_format_event_log_lists_entries():
    log = EventLog()
    fire_run_start(EventConfig(), log, 10, "cmd")
    text = format_event_log(log)
    assert "[1]" in text
    assert "run_start" in text


def test_event_log_clear():
    log = EventLog()
    fire_run_start(EventConfig(), log, 10, "cmd")
    log.clear()
    assert log.entries == []


def test_format_event_summary_empty():
    log = EventLog()
    assert format_event_summary(log) == "No events recorded."


def test_format_event_summary_counts():
    log = EventLog()
    cfg = EventConfig()
    fire_run_start(cfg, log, 10, "cmd")
    fire_run_end(cfg, log, 10, _result(rc=0))
    fire_run_start(cfg, log, 20, "cmd")
    fire_run_end(cfg, log, 20, _result(rc=1))
    summary = format_event_summary(log)
    assert "2 run_start" in summary
    assert "2 run_end" in summary
    assert "1 failed" in summary
