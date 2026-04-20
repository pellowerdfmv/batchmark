"""Console reporter for Notification objects."""

from typing import List

from batchmark.notifier import Notification

_LEVEL_LABEL = {
    "info": "INFO ",
    "warn": "WARN ",
    "fail": "FAIL ",
}

_LEVEL_PREFIX = {
    "info": "  ",
    "warn": "! ",
    "fail": "X ",
}


def format_notification(n: Notification) -> str:
    label = _LEVEL_LABEL.get(n.level, n.level.upper().ljust(5))
    prefix = _LEVEL_PREFIX.get(n.level, "  ")
    return f"{prefix}[{label}] {n.message}"


def format_notification_summary(notifications: List[Notification]) -> str:
    warns = sum(1 for n in notifications if n.level == "warn")
    fails = sum(1 for n in notifications if n.level == "fail")
    total = len(notifications)
    if total == 0:
        return "Notifications: none"
    parts = []
    if fails:
        parts.append(f"{fails} fail")
    if warns:
        parts.append(f"{warns} warn")
    return "Notifications: " + ", ".join(parts)


def print_notification_report(
    notifications: List[Notification],
    *,
    verbose: bool = False,
) -> None:
    if not notifications:
        if verbose:
            print("No threshold notifications.")
        return
    print("\n--- Threshold Notifications ---")
    for n in notifications:
        print(format_notification(n))
    print(format_notification_summary(notifications))
