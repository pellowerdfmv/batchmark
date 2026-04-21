"""Sliding-window aggregation over TimingResult lists."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult
from batchmark.stats import mean, stdev, min_duration, max_duration


@dataclass
class WindowResult:
    """Aggregated stats for a single sliding window."""
    window_index: int
    sizes: List[int]
    count: int
    successful: int
    mean_ms: Optional[float]
    stdev_ms: Optional[float]
    min_ms: Optional[float]
    max_ms: Optional[float]


@dataclass
class WindowConfig:
    size: int = 3          # number of results per window
    step: int = 1          # how many results to advance each window
    only_successful: bool = True


def _window_slices(results: List[TimingResult], cfg: WindowConfig) -> List[List[TimingResult]]:
    """Return overlapping slices of *results* according to *cfg*."""
    slices: List[List[TimingResult]] = []
    n = len(results)
    i = 0
    while i + cfg.size <= n:
        slices.append(results[i : i + cfg.size])
        i += cfg.step
    return slices


def compute_windows(
    results: List[TimingResult],
    cfg: Optional[WindowConfig] = None,
) -> List[WindowResult]:
    """Slide a window over *results* and return per-window aggregates."""
    if cfg is None:
        cfg = WindowConfig()

    slices = _window_slices(results, cfg)
    out: List[WindowResult] = []

    for idx, window in enumerate(slices):
        successful = [r for r in window if r.returncode == 0]
        subset = successful if cfg.only_successful else window

        out.append(
            WindowResult(
                window_index=idx,
                sizes=[r.size for r in window],
                count=len(window),
                successful=len(successful),
                mean_ms=mean(subset),
                stdev_ms=stdev(subset),
                min_ms=min_duration(subset),
                max_ms=max_duration(subset),
            )
        )

    return out


def format_window_summary(windows: List[WindowResult]) -> str:
    """Return a short human-readable summary of window statistics."""
    if not windows:
        return "No windows computed."
    lines = [f"Windows: {len(windows)}"]
    for w in windows:
        mean_str = f"{w.mean_ms:.1f} ms" if w.mean_ms is not None else "N/A"
        lines.append(
            f"  [{w.window_index}] sizes={w.sizes} "
            f"ok={w.successful}/{w.count} mean={mean_str}"
        )
    return "\n".join(lines)
