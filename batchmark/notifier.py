"""Notifier: emit alerts when timing results exceed thresholds."""

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class NotifyConfig:
    warn_above_ms: Optional[float] = None   # warn if mean duration exceeds this
    fail_above_ms: Optional[float] = None   # fail if mean duration exceeds this
    on_any_failure: bool = False             # alert if any run returned non-zero


@dataclass
class Notification:
    level: str          # "warn" | "fail" | "info"
    size: int
    message: str


def _mean_ms(results: List[TimingResult]) -> Optional[float]:
    durations = [r.duration for r in results if r.returncode == 0]
    if not durations:
        return None
    return sum(durations) * 1000.0 / len(durations)


def check_results(
    results: List[TimingResult],
    config: NotifyConfig,
) -> List[Notification]:
    """Inspect *results* (all from the same size) and return any notifications."""
    notifications: List[Notification] = []
    if not results:
        return notifications

    size = results[0].size

    if config.on_any_failure:
        failures = [r for r in results if r.returncode != 0]
        if failures:
            notifications.append(
                Notification(
                    level="fail",
                    size=size,
                    message=f"size={size}: {len(failures)} run(s) failed",
                )
            )

    mean = _mean_ms(results)
    if mean is None:
        return notifications

    if config.fail_above_ms is not None and mean > config.fail_above_ms:
        notifications.append(
            Notification(
                level="fail",
                size=size,
                message=(
                    f"size={size}: mean {mean:.1f} ms exceeds "
                    f"fail threshold {config.fail_above_ms:.1f} ms"
                ),
            )
        )
    elif config.warn_above_ms is not None and mean > config.warn_above_ms:
        notifications.append(
            Notification(
                level="warn",
                size=size,
                message=(
                    f"size={size}: mean {mean:.1f} ms exceeds "
                    f"warn threshold {config.warn_above_ms:.1f} ms"
                ),
            )
        )

    return notifications


def notify_all(
    results: List[TimingResult],
    config: NotifyConfig,
) -> List[Notification]:
    """Group *results* by size and collect all notifications."""
    from collections import defaultdict

    by_size: dict = defaultdict(list)
    for r in results:
        by_size[r.size].append(r)

    out: List[Notification] = []
    for size in sorted(by_size):
        out.extend(check_results(by_size[size], config))
    return out


def has_failures(notifications: List[Notification]) -> bool:
    """Return True if any notification in *notifications* has level ``'fail'``.

    Useful for callers that need to decide whether to exit with a non-zero
    status after collecting all notifications::

        notes = notify_all(results, config)
        if has_failures(notes):
            sys.exit(1)
    """
    return any(n.level == "fail" for n in notifications)
