"""CLI entry point for batchmark."""

import argparse
import sys
from typing import Optional, List

from batchmark.runner import run_batch
from batchmark.exporter import results_to_csv
from batchmark.reporter import print_results


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="batchmark",
        description="Benchmark shell commands across multiple input sizes.",
    )
    parser.add_argument(
        "command",
        help="Shell command template. Use {size} as placeholder.",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        required=True,
        metavar="N",
        help="List of input sizes to benchmark.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Number of runs per size (default: 3).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Timeout in seconds per run (default: none).",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        metavar="FILE",
        help="Export results to a CSV file.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress console output.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    try:
        results = run_batch(
            command_template=args.command,
            sizes=args.sizes,
            runs=args.runs,
            timeout=args.timeout,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print_results(results)

    if args.csv_path:
        try:
            results_to_csv(results, args.csv_path)
            if not args.quiet:
                print(f"\nResults written to {args.csv_path}")
        except OSError as exc:
            print(f"Error writing CSV: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
