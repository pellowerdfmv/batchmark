"""repeater.py — run each size a fixed number of times and collect all results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult, time_command


@dataclass
class RepeaterConfig:
    """Configuration for repeated runs."""
    repeats: int = 3
    stop_on_failure: bool = False
    timeout: Optional[float] = None


@dataclass
class RepeatGroup:
    """All timing results for a single (command, size) pair."""
    size: int
    command: str
    results: List[TimingResult] = field(default_factory=list)

    @property
    def total_runs(self) -> int:
        return len(self.results)

    @property
    def successful_runs(self) -> int:
        return sum(1 for r in self.results if r.returncode == 0)

    @property
    def failed_runs(self) -> int:
        return self.total_runs - self.successful_runs

    @property
    def mean_duration(self) -> Optional[float]:
        durations = [r.duration for r in self.results if r.returncode == 0]
        if not durations:
            return None
        return sum(durations) / len(durations)


def repeat_command(
    command: str,
    size: int,
    config: RepeaterConfig,
) -> RepeatGroup:
    """Run *command* the configured number of times and return a RepeatGroup."""
    group = RepeatGroup(size=size, command=command)
    for _ in range(config.repeats):
        result = time_command(command, timeout=config.timeout)
        group.results.append(result)
        if config.stop_on_failure and result.returncode != 0:
            break
    return group


def repeat_all(
    commands: List[tuple],  # list of (command_str, size)
    config: RepeaterConfig,
) -> List[RepeatGroup]:
    """Run repeat_command for every (command, size) pair."""
    return [repeat_command(cmd, size, config) for cmd, size in commands]


def format_repeat_summary(groups: List[RepeatGroup]) -> str:
    """Return a human-readable summary of all repeat groups."""
    lines = [f"{'Size':>8}  {'Runs':>5}  {'OK':>5}  {'Fail':>5}  {'Mean (ms)':>12}"]
    lines.append("-" * 44)
    for g in groups:
        mean = g.mean_duration
        mean_str = f"{mean * 1000:.2f}" if mean is not None else "N/A"
        lines.append(f"{g.size:>8}  {g.total_runs:>5}  {g.successful_runs:>5}  {g.failed_runs:>5}  {mean_str:>12}")
    return "\n".join(lines)
