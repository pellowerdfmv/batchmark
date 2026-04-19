"""Batch runner: executes a command template across multiple input sizes."""

from __future__ import annotations

import string
from typing import Iterable

from .timer import TimingResult, time_command


def build_command(template: str, size: int) -> str:
    """Substitute {size} placeholder in a command template.

    Args:
        template: Shell command string, e.g. ``"sort -R /dev/urandom | head -{size}"``.
        size: The input size value to substitute.

    Returns:
        The rendered command string.

    Raises:
        KeyError: If the template contains unknown placeholders.
    """
    return template.format(size=size)


def run_batch(
    command_template: str,
    sizes: Iterable[int],
    *,
    runs: int = 1,
    timeout: float | None = None,
    capture_output: bool = False,
) -> list[TimingResult]:
    """Run *command_template* for every value in *sizes*.

    Each size is run *runs* times.  Results are returned in the order they
    were executed.

    Args:
        command_template: Command with an optional ``{size}`` placeholder.
        sizes: Iterable of integer sizes to benchmark.
        runs: Number of repetitions per size (default 1).
        timeout: Per-run timeout in seconds passed to :func:`time_command`.
        capture_output: Whether to capture stdout/stderr.

    Returns:
        List of :class:`~batchmark.timer.TimingResult` instances.
    """
    if runs < 1:
        raise ValueError(f"runs must be >= 1, got {runs}")

    results: list[TimingResult] = []
    for size in sizes:
        cmd = build_command(command_template, size)
        for _ in range(runs):
            result = time_command(cmd, timeout=timeout, capture_output=capture_output)
            results.append(result)
    return results
