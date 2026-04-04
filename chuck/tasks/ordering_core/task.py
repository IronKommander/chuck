from __future__ import annotations

from heapq import merge
from random import Random
from typing import Any

from ...common import TaskSpec, checksum_ints


def generate(count: int, seed: int) -> list[int]:
    rng = Random(seed)
    return [rng.randrange(-1_000_000, 1_000_000) for _ in range(count)]


def solve(numbers: list[int], chunk_size: int = 1024) -> dict[str, Any]:
    chunks = [sorted(numbers[index : index + chunk_size]) for index in range(0, len(numbers), chunk_size)]
    merged = list(merge(*chunks)) if chunks else []
    middle = merged[len(merged) // 2] if merged else 0
    return {
        "count": len(merged),
        "min": merged[0] if merged else 0,
        "max": merged[-1] if merged else 0,
        "median": middle,
        "checksum": checksum_ints(merged),
    }


TASK_SPEC = TaskSpec("ordering_core", generate, solve, 128, 250_000)
