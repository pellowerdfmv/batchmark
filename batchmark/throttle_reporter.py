"""Reporter for throttle state — prints delay summary to stdout."""

from __future__ import annotations

from batchmark.throttle import ThrottleConfig, ThrottleState

_COL_WIDTH = 22


def format_throttle_header() -> str:
    cols = ["Delays Applied", "Delay Each (s)", "Total Wait (s)"]
    return "  ".join(c.ljust(_COL_WIDTH) for c in cols).rstrip()


def format_throttle_row(config: ThrottleConfig, state: ThrottleState) -> str:
    delay_each = f"{config.delay_seconds:.3f}" if config.enabled else "disabled"
    total = f"{state.total_delay_seconds:.3f}"
    cols = [
        str(state.delays_applied),
        delay_each,
        total,
    ]
    return "  ".join(c.ljust(_COL_WIDTH) for c in cols).rstrip()


def print_throttle_report(
    config: ThrottleConfig,
    state: ThrottleState,
) -> None:
    print("\n--- Throttle Report ---")
    print(format_throttle_header())
    print(format_throttle_row(config, state))
    if state.delays_applied > 0:
        print(
            f"\nTotal throttle overhead: {state.total_delay_seconds:.3f}s "
            f"across {state.delays_applied} gap(s)"
        )
    else:
        print("\nNo throttle delays were applied.")
