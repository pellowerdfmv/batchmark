"""High-level pipeline: optional warmup + filtered batch run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.filter import FilterConfig, filter_results
from batchmark.runner import run_batch
from batchmark.timer import TimingResult
from batchmark.warmup import WarmupConfig, run_warmup


@dataclass
class PipelineConfig:
    sizes: List[int]
    runs: int = 3
    timeout: Optional[float] = None
    warmup: WarmupConfig = field(default_factory=lambda: WarmupConfig(runs=0))
    filter: FilterConfig = field(default_factory=FilterConfig)


def run_and_filter(
    command: str,
    config: PipelineConfig,
) -> List[TimingResult]:
    """Run optional warmup, then benchmark, then apply filters."""
    for size in config.sizes:
        run_warmup(command, size=size, config=config.warmup, timeout=config.timeout)

    results = run_batch(
        command,
        sizes=config.sizes,
        runs=config.runs,
        timeout=config.timeout,
    )
    return filter_results(results, config.filter)
