"""Warmup runner: execute a command N times before actual benchmarking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from batchmark.timer import TimingResult, time_command


@dataclass
class WarmupConfig:
    runs: int = 1
    silent: bool = True


def run_warmup(
    command: str,
    size: int,
    config: WarmupConfig,
    timeout: float | None = None,
) -> List[TimingResult]:
    """Run *command* ``config.runs`` times as warmup.

    Returns the list of TimingResults so callers can inspect them if needed.
    Raises ``ValueError`` if ``config.runs`` is negative.
    """
    if config.runs < 0:
        raise ValueError(f"warmup runs must be >= 0, got {config.runs}")

    results: List[TimingResult] = []
    for _ in range(config.runs):
        result = time_command(command, size=size, timeout=timeout)
        results.append(result)
        if not config.silent and not result.success:
            print(f"[warmup] command failed with return code {result.returncode}")
    return results


def all_warmups_succeeded(results: List[TimingResult]) -> bool:
    """Return True only if every warmup run succeeded."""
    return all(r.success for r in results)
