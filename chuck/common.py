from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable

from .native_bindings import solve_with_backend


@dataclass(frozen=True)
class TaskSpec:
    name: str
    generator: Callable[[int, int], Any]
    solver: Callable[[Any], dict[str, Any]]
    regression_size: int
    benchmark_size: int
    algorithm_style: str = "deterministic"
    reliability_floor: float = 0.95


def checksum_ints(values: list[int]) -> int:
    total = 0
    for index, value in enumerate(values, start=1):
        total = (total + index * value) % 1_000_000_007
    return total


def round4(value: float) -> float:
    return round(value, 4)


def round6(value: float) -> float:
    return round(value, 6)


def benchmark_task(task: TaskSpec, seed: int, size: int | None = None) -> dict[str, Any]:
    actual_size = task.benchmark_size if size is None else size
    payload = task.generator(actual_size, seed)
    started = perf_counter()
    output = solve_with_backend(task=task, payload=payload)
    elapsed = perf_counter() - started
    return {"task": task.name, "size": actual_size, "seconds": round6(elapsed), "output": output}
