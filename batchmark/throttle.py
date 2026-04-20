"""Throttle: delay between benchmark runs to avoid resource contention."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List

from batchmark.timer import TimingResult


@dataclass
class ThrottleConfig:
    delay_seconds: float = 0.0
    enabled: bool = True


@dataclass
class ThrottleState:
    delays_applied: int = 0
    total_delay_seconds: float = 0.0
    _sleep_calls: List[float] = field(default_factory=list, repr=False)


def apply_delay(
    config: ThrottleConfig,
    state: ThrottleState,
    *,
    _sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Sleep for the configured delay and record it in state."""
    if not config.enabled or config.delay_seconds <= 0.0:
        return
    _sleep(config.delay_seconds)
    state.delays_applied += 1
    state.total_delay_seconds += config.delay_seconds
    state._sleep_calls.append(config.delay_seconds)


def throttle_results(
    results: List[TimingResult],
    config: ThrottleConfig,
    state: ThrottleState,
    *,
    _sleep: Callable[[float], None] = time.sleep,
) -> List[TimingResult]:
    """Apply a delay after each result except the last one."""
    for i, result in enumerate(results):
        if i < len(results) - 1:
            apply_delay(config, state, _sleep=_sleep)
    return results


def format_throttle_summary(state: ThrottleState) -> str:
    """Return a human-readable summary of throttle activity."""
    if state.delays_applied == 0:
        return "Throttle: no delays applied"
    return (
        f"Throttle: {state.delays_applied} delay(s) applied, "
        f"total wait {state.total_delay_seconds:.3f}s"
    )
