from __future__ import annotations

import argparse
from pathlib import Path

from .benchmark import format_benchmarks, run_benchmarks
from .comparison import (
    build_snapshot,
    compare_snapshots,
    format_comparison,
    format_verification,
    load_snapshot,
    verify_snapshot,
    write_snapshot,
)
from .regression import DEFAULT_REGRESSION_PATH, format_regression, generate_regression_file, run_regression


def main() -> int:
    parser = argparse.ArgumentParser(prog="chuck")
    subparsers = parser.add_subparsers(dest="command")

    bench_parser = subparsers.add_parser("bench", help="Run benchmarks")
    bench_parser.add_argument(
        "--task",
        choices=[
            "io_pipeline",
            "ordering_core",
            "retrieval_core",
            "data_encoding",
            "graph_analytics",
            "prime_analytics",
            "memory_tier",
            "memory_index",
            "compute_core",
            "relational_fusion",
        ],
        help="Run a single capability benchmark",
    )
    subparsers.add_parser("regress", help="Run regression checks")
    subparsers.add_parser("generate-baselines", help="Generate regression baselines")
    snapshot_parser = subparsers.add_parser("snapshot", help="Create a performance/reliability snapshot")
    snapshot_parser.add_argument("--label", required=True, help="Snapshot label (e.g. old, current)")
    snapshot_parser.add_argument("--iterations", type=int, default=5, help="Benchmark iterations per capability")
    snapshot_parser.add_argument(
        "--reliability-trials",
        type=int,
        default=200,
        help="Determinism/reliability checks per capability",
    )
    snapshot_parser.add_argument(
        "--backend",
        choices=["auto", "python", "cpp"],
        default="auto",
        help="Backend preference for snapshot runs",
    )
    snapshot_parser.add_argument("--out", help="Optional output path for snapshot JSON")

    compare_parser = subparsers.add_parser("compare", help="Compare old/new snapshots")
    compare_parser.add_argument("--old", required=True, help="Path to old snapshot JSON")
    compare_parser.add_argument("--new", help="Path to new snapshot JSON (optional with --run-current)")
    compare_parser.add_argument("--run-current", action="store_true", help="Build current snapshot before comparing")
    compare_parser.add_argument(
        "--label",
        default="current",
        help="Label used when --run-current is enabled",
    )
    compare_parser.add_argument("--iterations", type=int, default=5)
    compare_parser.add_argument("--reliability-trials", type=int, default=200)
    compare_parser.add_argument(
        "--backend",
        choices=["auto", "python", "cpp"],
        default="auto",
        help="Backend preference when using --run-current",
    )

    verify_parser = subparsers.add_parser("verify-snapshot", help="Verify snapshot provenance against current checkout")
    verify_parser.add_argument("--snapshot", required=True, help="Path to snapshot JSON")

    args = parser.parse_args()
    command = args.command or "bench"

    if command == "bench":
        print(format_benchmarks(run_benchmarks(task=args.task)))
        return 0
    if command == "regress":
        print(format_regression(run_regression()))
        return 0
    if command == "generate-baselines":
        path = generate_regression_file(DEFAULT_REGRESSION_PATH)
        print(f"Wrote baselines to {path}")
        return 0
    if command == "snapshot":
        snapshot = build_snapshot(
            label=args.label,
            iterations=args.iterations,
            reliability_trials=args.reliability_trials,
            backend=args.backend,
        )
        target = write_snapshot(snapshot, path=Path(args.out) if args.out else None)
        print(f"Wrote snapshot to {target}")
        return 0
    if command == "compare":
        old_snapshot = load_snapshot(Path(args.old))
        if args.run_current:
            generated = build_snapshot(
                label=args.label,
                iterations=args.iterations,
                reliability_trials=args.reliability_trials,
                backend=args.backend,
            )
            new_path = write_snapshot(generated)
            new_snapshot = generated
            print(f"Wrote current snapshot to {new_path}")
        elif args.new:
            new_snapshot = load_snapshot(Path(args.new))
        else:
            print("Please provide --new or use --run-current")
            return 1

        report = compare_snapshots(old_snapshot, new_snapshot)
        print(format_comparison(report))
        return 0
    if command == "verify-snapshot":
        snapshot = load_snapshot(Path(args.snapshot))
        result = verify_snapshot(snapshot)
        print(format_verification(result))
        return 0 if result["all_passed"] else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
