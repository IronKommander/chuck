from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .native_bindings import solve_with_backend
from .tasks import TASKS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGRESSION_PATH = ROOT / "data" / "regression.json"
DEFAULT_REGRESSION_DIR = ROOT / "data"


def _baseline_path(task_name: str) -> Path:
    return DEFAULT_REGRESSION_DIR / task_name / "regression.json"


def _expected_cases() -> list[dict[str, Any]]:
    cases = []
    for index, task in enumerate(TASKS, start=1):
        payload = task.generator(task.regression_size, index)
        cases.append(
            {
                "task": task.name,
                "seed": index,
                "size": task.regression_size,
                "expected": solve_with_backend(task=task, payload=payload, backend="python"),
            }
        )
    return cases


def generate_regression_file(path: Path | None = None) -> Path:
    target = DEFAULT_REGRESSION_PATH if path is None else path
    target.parent.mkdir(parents=True, exist_ok=True)

    manifest = []
    for entry in _expected_cases():
        baseline_file = _baseline_path(entry["task"])
        baseline_file.parent.mkdir(parents=True, exist_ok=True)
        baseline_file.write_text(json.dumps([entry], indent=2, sort_keys=True) + "\n", encoding="utf-8")
        manifest.append({"task": entry["task"], "path": str(baseline_file.relative_to(ROOT))})

    target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def load_regression_file(path: Path | None = None) -> list[dict[str, Any]]:
    target = DEFAULT_REGRESSION_PATH if path is None else path
    data = json.loads(target.read_text(encoding="utf-8"))
    if data and isinstance(data[0], dict) and "path" in data[0]:
        entries = []
        for item in data:
            entries.extend(json.loads((ROOT / item["path"]).read_text(encoding="utf-8")))
        return entries
    return data


def run_regression(path: Path | None = None) -> list[dict[str, Any]]:
    results = []
    entries = load_regression_file(path)
    task_map = {task.name: task for task in TASKS}
    for entry in entries:
        task = task_map[entry["task"]]
        payload = task.generator(entry["size"], entry["seed"])
        actual = solve_with_backend(task=task, payload=payload, backend="python")
        results.append(
            {
                "task": task.name,
                "passed": actual == entry["expected"],
                "expected": entry["expected"],
                "actual": actual,
            }
        )
    return results


def format_regression(results: list[dict[str, Any]]) -> str:
    lines = ["Regression summary:"]
    for result in results:
        state = "PASS" if result["passed"] else "FAIL"
        lines.append(f"- {result['task']}: {state}")
    return "\n".join(lines)
