from __future__ import annotations

import json
import platform
import subprocess
import sys
from hashlib import sha256
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from typing import Any

from .native_bindings import solve_with_backend
from .regression import DEFAULT_REGRESSION_PATH, load_regression_file
from .tasks import TASKS

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "data" / "reports" / "snapshots"


def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True)
            .strip()
        )
    except Exception:
        return "unknown"


def _git_tree() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True)
            .strip()
        )
    except Exception:
        return "unknown"


def _git_dirty() -> bool:
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
        return bool(status.strip())
    except Exception:
        return True


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _code_fingerprint() -> str:
    digest = sha256()
    candidates: list[Path] = []
    candidates.extend((ROOT / "chuck" / "tasks").glob("**/*.py"))
    candidates.extend((ROOT / "chuck" / "benchmarks").glob("**/*.py"))
    candidates.extend(
        [
            ROOT / "chuck" / "common.py",
            ROOT / "chuck" / "benchmark.py",
            ROOT / "chuck" / "regression.py",
            ROOT / "chuck" / "comparison.py",
        ]
    )

    seen: set[Path] = set()
    for file_path in sorted(path for path in candidates if path.exists()):
        if file_path in seen:
            continue
        seen.add(file_path)
        digest.update(str(file_path.relative_to(ROOT)).encode("utf-8"))
        digest.update(_sha256_file(file_path).encode("utf-8"))
    return digest.hexdigest()


def _baseline_fingerprint() -> str:
    digest = sha256()
    manifest_path = ROOT / "data" / "regression.json"
    if not manifest_path.exists():
        return "missing"

    digest.update(_sha256_file(manifest_path).encode("utf-8"))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return "invalid"

    for entry in manifest:
        path_text = entry.get("path", "")
        baseline_path = ROOT / path_text
        digest.update(path_text.encode("utf-8"))
        if baseline_path.exists():
            digest.update(_sha256_file(baseline_path).encode("utf-8"))
        else:
            digest.update(b"missing")
    return digest.hexdigest()


def _load_expected_by_task() -> dict[str, dict[str, Any]]:
    entries = load_regression_file(DEFAULT_REGRESSION_PATH)
    expected: dict[str, dict[str, Any]] = {}
    for entry in entries:
        expected[entry["task"]] = entry
    return expected


def _measure_benchmark(task: Any, iterations: int, backend: str) -> dict[str, Any]:
    samples: list[float] = []
    last_output: dict[str, Any] = {}
    backend_counts: dict[str, int] = {}
    for index in range(iterations):
        payload = task.generator(task.benchmark_size, 10_000 + index)
        started = perf_counter()
        last_output = solve_with_backend(task=task, payload=payload, backend=backend)
        samples.append(perf_counter() - started)
        actual_backend = str(last_output.get("backend", "unknown"))
        backend_counts[actual_backend] = backend_counts.get(actual_backend, 0) + 1

    return {
        "samples_seconds": [round(sample, 6) for sample in samples],
        "mean_seconds": round(mean(samples), 6),
        "median_seconds": round(median(samples), 6),
        "backend_counts": backend_counts,
        "last_output": last_output,
    }


def _measure_reliability(task: Any, expected: dict[str, Any] | None, trials: int, backend: str) -> dict[str, Any]:
    passed = 0.0
    total = 0
    baseline_passed = False
    backend_counts: dict[str, int] = {}

    def _track_backend(result: dict[str, Any]) -> None:
        actual_backend = str(result.get("backend", "unknown"))
        backend_counts[actual_backend] = backend_counts.get(actual_backend, 0) + 1

    if expected is not None:
        total += 1
        try:
            payload = task.generator(expected["size"], expected["seed"])
            baseline_result = solve_with_backend(task=task, payload=payload, backend=backend)
            _track_backend(baseline_result)
            baseline_passed = baseline_result == expected["expected"]
            if baseline_passed:
                passed += 1
        except Exception:
            baseline_passed = False

    for index in range(trials):
        total += 1
        seed = 50_000 + index
        try:
            payload = task.generator(task.regression_size, seed)
            first = solve_with_backend(task=task, payload=payload, backend=backend)
            _track_backend(first)
            if task.algorithm_style == "probabilistic":
                confidence = float(first.get("confidence", task.reliability_floor))
                confidence = max(0.0, min(1.0, confidence))
                passed += confidence
            else:
                second = solve_with_backend(task=task, payload=payload, backend=backend)
                _track_backend(second)
                if first == second:
                    passed += 1
        except Exception:
            continue

    score = passed / total if total else 0.0
    return {
        "score": round(score, 6),
        "passed_checks": passed,
        "total_checks": total,
        "baseline_passed": baseline_passed,
        "backend_counts": backend_counts,
    }


def build_snapshot(label: str, iterations: int = 5, reliability_trials: int = 200, backend: str = "auto") -> dict[str, Any]:
    expected_by_task = _load_expected_by_task()
    tasks: dict[str, Any] = {}

    for task in TASKS:
        benchmark = _measure_benchmark(task, iterations=iterations, backend=backend)
        reliability = _measure_reliability(
            task,
            expected=expected_by_task.get(task.name),
            trials=reliability_trials,
            backend=backend,
        )
        tasks[task.name] = {"benchmark": benchmark, "reliability": reliability}

    return {
        "meta": {
            "label": label,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cpu": platform.processor() or "unknown",
            "iterations": iterations,
            "reliability_trials": reliability_trials,
            "backend_preference": backend,
            "git_commit": _git_commit(),
            "git_tree": _git_tree(),
            "git_dirty": _git_dirty(),
            "code_fingerprint": _code_fingerprint(),
            "baseline_fingerprint": _baseline_fingerprint(),
        },
        "tasks": tasks,
    }


def write_snapshot(snapshot: dict[str, Any], path: Path | None = None) -> Path:
    target = path
    if target is None:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        label = snapshot["meta"]["label"]
        target = SNAPSHOT_DIR / f"{label}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def load_snapshot(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_snapshots(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    task_names = sorted(set(old["tasks"].keys()) & set(new["tasks"].keys()))
    rows = []
    speedups = []

    for task_name in task_names:
        old_task = old["tasks"][task_name]
        new_task = new["tasks"][task_name]

        old_time = old_task["benchmark"]["median_seconds"]
        new_time = new_task["benchmark"]["median_seconds"]
        old_rel = old_task["reliability"]["score"]
        new_rel = new_task["reliability"]["score"]

        speedup = (old_time / new_time) if new_time else 0.0
        delta_pct = ((new_time - old_time) / old_time * 100.0) if old_time else 0.0
        rel_delta = new_rel - old_rel
        speedups.append(speedup)

        rows.append(
            {
                "task": task_name,
                "old_median_seconds": old_time,
                "new_median_seconds": new_time,
                "speedup_x": round(speedup, 4),
                "time_delta_percent": round(delta_pct, 2),
                "old_reliability": old_rel,
                "new_reliability": new_rel,
                "reliability_delta": round(rel_delta, 6),
            }
        )

    avg_speedup = round(mean(speedups), 4) if speedups else 0.0
    old_meta = old.get("meta", {})
    new_meta = new.get("meta", {})
    same_system = (
        old_meta.get("platform") == new_meta.get("platform")
        and old_meta.get("python") == new_meta.get("python")
        and old_meta.get("cpu") == new_meta.get("cpu")
    )
    same_backend_preference = old_meta.get("backend_preference") == new_meta.get("backend_preference")

    return {
        "meta": {
            "old_label": old_meta.get("label", "old"),
            "new_label": new_meta.get("label", "new"),
            "same_system": same_system,
            "same_backend_preference": same_backend_preference,
            "old_backend_preference": old_meta.get("backend_preference", "auto"),
            "new_backend_preference": new_meta.get("backend_preference", "auto"),
            "old_commit": old_meta.get("git_commit", "unknown"),
            "new_commit": new_meta.get("git_commit", "unknown"),
            "old_dirty": old_meta.get("git_dirty", True),
            "new_dirty": new_meta.get("git_dirty", True),
        },
        "summary": {
            "task_count": len(rows),
            "average_speedup_x": avg_speedup,
        },
        "rows": rows,
    }


def format_comparison(report: dict[str, Any]) -> str:
    lines = [
        "A/B Comparison:",
        f"- old: {report['meta']['old_label']} ({report['meta']['old_commit']})",
        f"- new: {report['meta']['new_label']} ({report['meta']['new_commit']})",
        f"- same system: {report['meta']['same_system']}",
        (
            "- backend preference: "
            f"{report['meta']['old_backend_preference']} -> {report['meta']['new_backend_preference']} "
            f"(same={report['meta']['same_backend_preference']})"
        ),
        f"- old snapshot clean checkout: {not report['meta']['old_dirty']}",
        f"- new snapshot clean checkout: {not report['meta']['new_dirty']}",
        f"- average speedup: {report['summary']['average_speedup_x']}x",
        "",
        "Per capability:",
    ]

    for row in report["rows"]:
        lines.append(
            "- "
            f"{row['task']}: "
            f"{row['old_median_seconds']}s -> {row['new_median_seconds']}s, "
            f"speedup {row['speedup_x']}x, "
            f"delta {row['time_delta_percent']}%, "
            f"reliability {row['old_reliability']} -> {row['new_reliability']} ({row['reliability_delta']:+.6f})"
        )
    return "\n".join(lines)


def verify_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    meta = snapshot.get("meta", {})
    checks = {
        "commit_matches": meta.get("git_commit") == _git_commit(),
        "tree_matches": meta.get("git_tree") == _git_tree(),
        "code_fingerprint_matches": meta.get("code_fingerprint") == _code_fingerprint(),
        "baseline_fingerprint_matches": meta.get("baseline_fingerprint") == _baseline_fingerprint(),
        "snapshot_recorded_clean": meta.get("git_dirty") is False,
    }
    checks["all_passed"] = all(checks.values())
    return checks


def format_verification(result: dict[str, Any]) -> str:
    lines = ["Snapshot verification:"]
    lines.append(f"- commit matches current checkout: {result['commit_matches']}")
    lines.append(f"- tree matches current checkout: {result['tree_matches']}")
    lines.append(f"- code fingerprint matches: {result['code_fingerprint_matches']}")
    lines.append(f"- baseline fingerprint matches: {result['baseline_fingerprint_matches']}")
    lines.append(f"- snapshot recorded as clean checkout: {result['snapshot_recorded_clean']}")
    lines.append(f"- all checks passed: {result['all_passed']}")
    return "\n".join(lines)
