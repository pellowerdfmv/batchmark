"""Command-line interface for batchmark."""

import argparse
import sys
from pathlib import Path

from batchmark.runner import run_batch
from batchmark.exporter import results_to_csv


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="batchmark",
        description="Benchmark shell commands across multiple input sizes.",
    )
    parser.add_argument(
        "command",
        help="Command template to benchmark. Use {size} as a placeholder.",
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
        metavar="N",
        help="Number of runs per size (default: 3).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Timeout in seconds per run.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write CSV results to FILE.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-run output.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    results = run_batch(
        args.command,
        sizes=args.sizes,
        runs=args.runs,
        timeout=args.timeout,
    )

    if not args.quiet:
        print(f"{'size':>10}  {'run':>4}  {'elapsed':>10}  {'returncode':>10}")
        print("-" * 42)
        for r in results:
            print(f"{r.size:>10}  {r.run:>4}  {r.elapsed:>10.4f}  {r.returncode:>10}")

    if args.output:
        results_to_csv(results, args.output)
        if not args.quiet:
            print(f"\nResults written to {args.output}")

    failed = [r for r in results if r.returncode != 0]
    if failed:
        print(f"\nWarning: {len(failed)} run(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
