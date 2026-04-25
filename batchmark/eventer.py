"""Event hooks for batchmark pipeline lifecycle."""
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from batchmark.timer import TimingResult


@dataclass
class EventConfig:
    on_run_start: Optional[Callable[[int, str], None]] = None
    on_run_end: Optional[Callable[[int, TimingResult], None]] = None
    on_batch_start: Optional[Callable[[List[int]], None]] = None
    on_batch_end: Optional[Callable[[List[TimingResult]], None]] = None


@dataclass
class EventLog:
    entries: List[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        self.entries.append(message)

    def clear(self) -> None:
        self.entries.clear()


def fire_run_start(
    config: EventConfig, log: EventLog, size: int, command: str
) -> None:
    log.add(f"run_start: size={size} cmd={command}")
    if config.on_run_start is not None:
        config.on_run_start(size, command)


def fire_run_end(
    config: EventConfig, log: EventLog, size: int, result: TimingResult
) -> None:
    status = "ok" if result.returncode == 0 else "fail"
    log.add(f"run_end: size={size} status={status} duration={result.duration:.4f}")
    if config.on_run_end is not None:
        config.on_run_end(size, result)


def fire_batch_start(
    config: EventConfig, log: EventLog, sizes: List[int]
) -> None:
    log.add(f"batch_start: sizes={sizes}")
    if config.on_batch_start is not None:
        config.on_batch_start(sizes)


def fire_batch_end(
    config: EventConfig, log: EventLog, results: List[TimingResult]
) -> None:
    log.add(f"batch_end: count={len(results)}")
    if config.on_batch_end is not None:
        config.on_batch_end(results)


def format_event_log(log: EventLog) -> str:
    if not log.entries:
        return "(no events)"
    lines = [f"  [{i + 1}] {e}" for i, e in enumerate(log.entries)]
    return "Event log:\n" + "\n".join(lines)
