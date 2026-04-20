"""Budget enforcement: abort a batch run if cumulative time exceeds a limit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class BudgetConfig:
    """Configuration for a time budget."""

    max_total_seconds: Optional[float] = None  # None means no limit


@dataclass
class BudgetState:
    """Mutable state tracking elapsed budget."""

    config: BudgetConfig
    _elapsed: float = field(default=0.0, init=False)

    def record(self, result: TimingResult) -> None:
        """Add the duration of a result to the running total.

        Only successful (non-negative) durations count toward the budget.
        """
        if result.duration >= 0.0:
            self._elapsed += result.duration

    @property
    def elapsed(self) -> float:
        """Total elapsed seconds recorded so far."""
        return self._elapsed

    def is_exceeded(self) -> bool:
        """Return True if the budget has been exceeded."""
        if self.config.max_total_seconds is None:
            return False
        return self._elapsed > self.config.max_total_seconds

    def remaining(self) -> Optional[float]:
        """Seconds remaining in the budget, or None if no budget is set."""
        if self.config.max_total_seconds is None:
            return None
        return max(0.0, self.config.max_total_seconds - self._elapsed)


def apply_budget(
    results: List[TimingResult],
    config: BudgetConfig,
) -> List[TimingResult]:
    """Return only the results that fit within the budget.

    Results are consumed in order; as soon as the running total exceeds
    ``max_total_seconds`` the remaining results are dropped.
    """
    if config.max_total_seconds is None:
        return list(results)

    state = BudgetState(config=config)
    kept: List[TimingResult] = []
    for r in results:
        state.record(r)
        kept.append(r)
        if state.is_exceeded():
            break
    return kept
