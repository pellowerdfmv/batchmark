"""Sorting utilities for TimingResult lists."""

from typing import List, Callable
from batchmark.timer import TimingResult

_SORT_KEYS = {
    "size": lambda r: r.size,
    "duration": lambda r: r.duration if r.duration >= 0 else float("inf"),
    "returncode": lambda r: r.returncode,
    "label": lambda r: (r.label or ""),
}


def available_sort_keys() -> List[str]:
    """Return the list of valid sort key names."""
    return list(_SORT_KEYS.keys())


def sort_results(
    results: List[TimingResult],
    key: str = "size",
    reverse: bool = False,
) -> List[TimingResult]:
    """Return a new list of results sorted by *key*.

    Parameters
    ----------
    results:
        Source list; not mutated.
    key:
        One of ``'size'``, ``'duration'``, ``'returncode'``, ``'label'``.
    reverse:
        If ``True``, sort in descending order.

    Raises
    ------
    ValueError
        If *key* is not a recognised sort key.
    """
    if key not in _SORT_KEYS:
        raise ValueError(
            f"Unknown sort key {key!r}. Choose from: {available_sort_keys()}"
        )
    fn: Callable[[TimingResult], object] = _SORT_KEYS[key]
    return sorted(results, key=fn, reverse=reverse)
