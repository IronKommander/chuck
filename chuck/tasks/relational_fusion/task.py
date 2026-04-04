from __future__ import annotations

from collections import defaultdict
from random import Random
from typing import Any

from ...common import TaskSpec


def generate(row_count: int, seed: int) -> dict[str, Any]:
    rng = Random(seed)
    key_count = max(8, row_count // 4 or 8)
    keys = [f"k{index:03d}" for index in range(key_count)]
    left = [(keys[rng.randrange(key_count)], rng.randrange(1, 1_000)) for _ in range(row_count)]
    right = [(keys[rng.randrange(key_count)], rng.randrange(1, 1_000)) for _ in range(max(4, row_count // 2 or 4))]
    return {"left": left, "right": right}


def solve(payload: dict[str, Any]) -> dict[str, Any]:
    left = payload["left"]
    right = payload["right"]
    index: dict[str, list[int]] = defaultdict(list)
    for key, value in right:
        index[key].append(value)

    join_rows = 0
    aggregate = 0
    for key, left_value in left:
        for right_value in index.get(key, []):
            join_rows += 1
            aggregate += left_value + right_value
    return {
        "left_rows": len(left),
        "right_rows": len(right),
        "join_rows": join_rows,
        "aggregate": aggregate,
    }


TASK_SPEC = TaskSpec("relational_fusion", generate, solve, 128, 40_000)
