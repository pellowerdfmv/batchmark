"""capper.py — clamp result durations to a configurable ceiling.

Any result whose duration exceeds *max_ms* is replaced with a capped copy
whose duration equals *max_ms* and whose ``capped`` flag is set to True.
Results that already failed (success=False) are passed through unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from batchmark.timer import TimingResult


@dataclass
class CappedResult:
    """A TimingResult decorated with capping metadata."""

    result: TimingResult
    capped: bool
    original_duration: float  # seconds, always the raw value

    # Convenience proxies so downstream code can treat this like TimingResult.
    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


@dataclass
class CapperConfig:
    """Configuration for the duration capper."""

    max_ms: float | None = None  # None means no cap applied


def _clamp(result: TimingResult, max_s: float) -> TimingResult:
    """Return a new TimingResult with duration clamped to *max_s*."""
    return TimingResult(
        size=result.size,
        command=result.command,
        duration=max_s,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def cap_results(
    results: List[TimingResult], config: CapperConfig
) -> List[CappedResult]:
    """Apply the duration cap described by *config* to every result.

    Parameters
    ----------
    results:
        Raw timing results from a benchmark run.
    config:
        Capper configuration.  If ``max_ms`` is None or non-positive the
        results are wrapped without modification.

    Returns
    -------
    List[CappedResult]
        One entry per input result, in the same order.
    """
    max_s = (config.max_ms / 1000.0) if (config.max_ms and config.max_ms > 0) else None
    out: List[CappedResult] = []
    for r in results:
        original = r.duration
        if max_s is not None and r.returncode == 0 and r.duration > max_s:
            clamped = _clamp(r, max_s)
            out.append(CappedResult(result=clamped, capped=True, original_duration=original))
        else:
            out.append(CappedResult(result=r, capped=False, original_duration=original))
    return out


def format_cap_summary(capped: List[CappedResult], config: CapperConfig) -> str:
    """Return a one-line human-readable summary of capping activity."""
    n_capped = sum(1 for c in capped if c.capped)
    if config.max_ms is None or config.max_ms <= 0:
        return "Capper: disabled"
    return (
        f"Capper: max={config.max_ms:.0f} ms  "
        f"capped={n_capped}/{len(capped)}"
    )
