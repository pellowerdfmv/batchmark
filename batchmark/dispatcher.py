"""Dispatcher: route results to named handlers based on size ranges."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from batchmark.timer import TimingResult


@dataclass
class DispatchConfig:
    """Maps size ranges to handler names.

    Each rule is (min_size, max_size, handler_name).  Ranges are inclusive.
    Results that match no rule receive *default_handler*.
    """
    rules: List[Tuple[int, int, str]] = field(default_factory=list)
    default_handler: str = "default"


@dataclass
class DispatchedResult:
    result: TimingResult
    handler: str

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _find_handler(size: int, config: DispatchConfig) -> str:
    for lo, hi, name in config.rules:
        if lo <= size <= hi:
            return name
    return config.default_handler


def dispatch_results(
    results: List[TimingResult],
    config: Optional[DispatchConfig] = None,
) -> List[DispatchedResult]:
    """Assign a handler name to every result according to *config*."""
    cfg = config or DispatchConfig()
    return [DispatchedResult(result=r, handler=_find_handler(r.size, cfg)) for r in results]


def group_by_handler(
    dispatched: List[DispatchedResult],
) -> Dict[str, List[DispatchedResult]]:
    """Return a dict mapping handler name -> list of DispatchedResult."""
    groups: Dict[str, List[DispatchedResult]] = {}
    for dr in dispatched:
        groups.setdefault(dr.handler, []).append(dr)
    return groups


def format_dispatch_summary(dispatched: List[DispatchedResult]) -> str:
    groups = group_by_handler(dispatched)
    lines = [f"Dispatched {len(dispatched)} result(s) to {len(groups)} handler(s):"]
    for name, items in sorted(groups.items()):
        lines.append(f"  {name}: {len(items)} result(s)")
    return "\n".join(lines)
