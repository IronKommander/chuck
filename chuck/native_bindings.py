from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .common import TaskSpec


ROOT = Path(__file__).resolve().parents[1]
NATIVE_BUILD_DIR = ROOT / "native" / "cpp" / "build"

if NATIVE_BUILD_DIR.exists():
    native_build_text = str(NATIVE_BUILD_DIR)
    if native_build_text not in sys.path:
        sys.path.insert(0, native_build_text)


_TASK_TO_SYMBOL = {
    "io_pipeline": "solve_io_pipeline",
    "ordering_core": "solve_ordering_core",
    "retrieval_core": "solve_retrieval_core",
    "data_encoding": "solve_data_encoding",
    "graph_analytics": "solve_graph_analytics",
    "prime_analytics": "solve_prime_analytics",
    "memory_tier": "solve_memory_tier",
    "memory_index": "solve_memory_index",
    "compute_core": "solve_compute_core",
    "relational_fusion": "solve_relational_fusion",
}


def _cpp_module_candidates(task_name: str) -> list[str]:
    return [
        f"chuck_cpp_{task_name}",
        f"chuck.tasks.{task_name}.native_cpp.binding",
    ]


def _native_solver(task_name: str, backend: str) -> Any | None:
    if backend == "cpp":
        symbol_candidates = ["solve", _TASK_TO_SYMBOL.get(task_name, "")]
        for module_name in _cpp_module_candidates(task_name):
            try:
                module = import_module(module_name)
            except Exception:
                continue
            for symbol in symbol_candidates:
                if symbol:
                    solver = getattr(module, symbol, None)
                    if solver is not None:
                        return solver
        return None

    return None


def solve_with_backend(task: TaskSpec, payload: Any, backend: str = "auto") -> dict[str, Any]:
    if backend == "python":
        result = task.solver(payload)
        result.setdefault("backend", "python")
        return result

    backends = ["cpp"] if backend == "auto" else [backend]
    for item in backends:
        solver = _native_solver(task.name, item)
        if solver is None:
            continue
        try:
            result = solver(payload)
            if isinstance(result, dict):
                result.setdefault("backend", item)
                return result
        except Exception:
            continue

    result = task.solver(payload)
    result.setdefault("backend", "python")
    return result
