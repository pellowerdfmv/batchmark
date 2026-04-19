"""High-level pipeline: run a batch and optionally filter the results."""

from typing import List, Optional

from batchmark.runner import run_batch
from batchmark.timer import TimingResult
from batchmark.filter import filter_results


def run_and_filter(
    template: str,
    sizes: List[int],
    runs: int = 1,
    timeout: Optional[float] = None,
    *,
    only_success: bool = False,
    max_duration: Optional[float] = None,
    filter_sizes: Optional[List[int]] = None,
) -> List[TimingResult]:
    """Run *template* for every size in *sizes* and apply result filters.

    Parameters
    ----------
    template:     Command template passed to :func:`run_batch`.
    sizes:        Input sizes to benchmark.
    runs:         Number of repetitions per size.
    timeout:      Per-run timeout in seconds (None = no limit).
    only_success: Discard results with non-zero return-code.
    max_duration: Discard results that took longer than this many seconds.
    filter_sizes: If given, keep only results for these specific sizes.

    Returns
    -------
    Filtered list of :class:`~batchmark.timer.TimingResult` objects.
    """
    raw: List[TimingResult] = run_batch(
        template=template,
        sizes=sizes,
        runs=runs,
        timeout=timeout,
    )
    return filter_results(
        raw,
        sizes=filter_sizes,
        only_success=only_success,
        max_duration=max_duration,
    )
