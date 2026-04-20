"""Runner that integrates checkpoint save/resume into batch execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.checkpoint import (
    already_run,
    append_entry,
    load_checkpoint,
    results_from_checkpoint,
)
from batchmark.runner import build_command
from batchmark.timer import TimingResult, time_command


@dataclass
class CheckpointRunnerConfig:
    command_template: str
    sizes: List[int]
    runs: int = 3
    timeout: Optional[float] = None
    checkpoint_path: Optional[str] = None


def run_with_checkpoint(
    config: CheckpointRunnerConfig,
) -> Dict[int, List[TimingResult]]:
    """Run benchmarks for each size, skipping already-checkpointed runs.

    Returns a mapping of size -> list of TimingResults.
    """
    entries = []
    if config.checkpoint_path:
        entries = load_checkpoint(config.checkpoint_path)

    results: Dict[int, List[TimingResult]] = {}

    for size in config.sizes:
        size_results: List[TimingResult] = []

        # Recover any already-completed runs from checkpoint
        recovered = results_from_checkpoint(entries, size)
        size_results.extend(recovered)

        for run_idx in range(config.runs):
            if already_run(entries, size, run_idx):
                continue

            cmd = build_command(config.command_template, size)
            result = time_command(cmd, timeout=config.timeout)

            size_results.append(result)

            if config.checkpoint_path:
                entries = append_entry(
                    config.checkpoint_path, entries, size, run_idx, result
                )

        results[size] = size_results

    return results
