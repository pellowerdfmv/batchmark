"""stacker.py – stack multiple benchmark result sets by label for side-by-side comparison."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict

from batchmark.timer import TimingResult


@dataclass
class StackedRow:
    size: int
    label: str
    run_index: int
    duration: Optional[float]  # seconds, None if failed
    success: bool
    returncode: int


@dataclass
class StackConfig:
    labels: List[str] = field(default_factory=list)
    default_label: str = "unlabeled"


def _label_for(index: int, config: StackConfig) -> str:
    if index < len(config.labels):
        return config.labels[index]
    return config.default_label


def stack_results(
    result_sets: List[List[TimingResult]],
    config: Optional[StackConfig] = None,
) -> List[StackedRow]:
    """Flatten multiple result sets into a single list of StackedRows.

    Each result set is assigned the label from *config.labels* at the
    corresponding position, falling back to *config.default_label*.
    Within each set the results are enumerated to produce a per-size
    run index.
    """
    if config is None:
        config = StackConfig()

    rows: List[StackedRow] = []
    for set_index, result_set in enumerate(result_sets):
        label = _label_for(set_index, config)
        # track per-size run index within this set
        size_counter: Dict[int, int] = {}
        for result in result_set:
            idx = size_counter.get(result.size, 0)
            size_counter[result.size] = idx + 1
            dur = result.duration if result.returncode == 0 else None
            rows.append(
                StackedRow(
                    size=result.size,
                    label=label,
                    run_index=idx,
                    duration=dur,
                    success=result.returncode == 0,
                    returncode=result.returncode,
                )
            )
    return rows


def format_stack_summary(rows: List[StackedRow]) -> str:
    """Return a short human-readable summary of the stacked results."""
    if not rows:
        return "No stacked results."
    labels = sorted({r.label for r in rows})
    sizes = sorted({r.size for r in rows})
    total = len(rows)
    ok = sum(1 for r in rows if r.success)
    lines = [
        f"Stacked results: {total} rows, {ok} successful, {total - ok} failed",
        f"Labels : {', '.join(labels)}",
        f"Sizes  : {', '.join(str(s) for s in sizes)}",
    ]
    return "\n".join(lines)
