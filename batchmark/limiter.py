"""Rate limiter for batchmark: throttle command execution with configurable delays."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from batchmark.timer import TimingResult


@dataclass
class LimiterConfig:
    """Configuration for rate-limiting batch runs."""
    delay_seconds: float = 0.0          # fixed pause between each run
    max_runs_per_minute: Optional[int] = None  # if set, enforces a per-minute cap
    jitter_seconds: float = 0.0         # random jitter added on top of delay


@dataclass
class _RateState:
    """Internal sliding-window state for per-minute limiting."""
    timestamps: List[float] = field(default_factory=list)

    def record(self, ts: float) -> None:
        self.timestamps.append(ts)
        cutoff = ts - 60.0
        self.timestamps = [t for t in self.timestamps if t >= cutoff]

    def count_in_window(self, now: float) -> int:
        cutoff = now - 60.0
        return sum(1 for t in self.timestamps if t >= cutoff)


def _sleep(seconds: float) -> None:  # pragma: no cover – thin wrapper for testability
    if seconds > 0:
        time.sleep(seconds)


def apply_delay(
    config: LimiterConfig,
    state: _RateState,
    *,
    sleep_fn: Callable[[float], None] = _sleep,
    now_fn: Callable[[], float] = time.monotonic,
    random_fn: Callable[[], float] = __import__('random').random,
) -> None:
    """Block until rate-limit constraints are satisfied, then record the run."""
    if config.max_runs_per_minute is not None:
        while True:
            now = now_fn()
            if state.count_in_window(now) < config.max_runs_per_minute:
                break
            sleep_fn(0.1)

    pause = config.delay_seconds
    if config.jitter_seconds > 0:
        pause += random_fn() * config.jitter_seconds
    sleep_fn(pause)

    state.record(now_fn())


def run_with_limit(
    results: List[TimingResult],
    config: LimiterConfig,
    *,
    sleep_fn: Callable[[float], None] = _sleep,
    now_fn: Callable[[], float] = time.monotonic,
) -> List[TimingResult]:
    """Re-yield *results* inserting rate-limit delays between each entry.

    In real usage the caller would interleave this with command execution;
    here we model the delay pass-through so tests can verify ordering and
    that the state is updated correctly.
    """
    state = _RateState()
    limited: List[TimingResult] = []
    for i, result in enumerate(results):
        if i > 0:  # no delay before the very first run
            apply_delay(config, state, sleep_fn=sleep_fn, now_fn=now_fn)
        else:
            state.record(now_fn())
        limited.append(result)
    return limited
