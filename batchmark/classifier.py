"""Classify timing results into performance tiers based on configurable thresholds."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class ClassifierConfig:
    """Thresholds (in seconds) separating performance classes."""
    fast_below: float = 0.1   # duration < fast_below  -> "fast"
    slow_above: float = 1.0   # duration >= slow_above -> "slow"
    # fast_below <= duration < slow_above              -> "medium"
    labels: dict = field(default_factory=lambda: {
        "fast": "fast",
        "medium": "medium",
        "slow": "slow",
        "failed": "failed",
    })


@dataclass
class ClassifiedResult:
    result: TimingResult
    classification: str

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> Optional[float]:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


def _classify(result: TimingResult, config: ClassifierConfig) -> str:
    if result.returncode != 0:
        return config.labels["failed"]
    d = result.duration or 0.0
    if d < config.fast_below:
        return config.labels["fast"]
    if d >= config.slow_above:
        return config.labels["slow"]
    return config.labels["medium"]


def classify_results(
    results: List[TimingResult],
    config: Optional[ClassifierConfig] = None,
) -> List[ClassifiedResult]:
    """Return a ClassifiedResult for every input result."""
    cfg = config or ClassifierConfig()
    return [ClassifiedResult(result=r, classification=_classify(r, cfg)) for r in results]


def format_classification_summary(classified: List[ClassifiedResult]) -> str:
    counts: dict = {}
    for c in classified:
        counts[c.classification] = counts.get(c.classification, 0) + 1
    parts = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    return f"Classification summary — {parts}" if parts else "Classification summary — (no results)"
