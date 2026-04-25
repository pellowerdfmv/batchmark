"""Reporter for event log output."""
from batchmark.eventer import EventLog, format_event_log


def print_event_log(log: EventLog) -> None:
    """Print the full event log to stdout."""
    print(format_event_log(log))


def format_event_summary(log: EventLog) -> str:
    """Return a one-line summary of recorded events."""
    total = len(log.entries)
    if total == 0:
        return "No events recorded."
    starts = sum(1 for e in log.entries if e.startswith("run_start"))
    ends = sum(1 for e in log.entries if e.startswith("run_end"))
    fails = sum(
        1 for e in log.entries if e.startswith("run_end") and "status=fail" in e
    )
    return (
        f"Events: {total} total | "
        f"{starts} run_start | {ends} run_end | {fails} failed"
    )


def print_event_summary(log: EventLog) -> None:
    """Print the event summary to stdout."""
    print(format_event_summary(log))
