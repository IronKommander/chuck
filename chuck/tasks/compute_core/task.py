from __future__ import annotations

from random import Random
from typing import Any

from ...common import TaskSpec


def generate(size: int, seed: int) -> dict[str, Any]:
    rng = Random(seed)
    left = [[rng.randrange(0, 10) for _ in range(size)] for _ in range(size)]
    right = [[rng.randrange(0, 10) for _ in range(size)] for _ in range(size)]
    return {"left": left, "right": right, "block_size": max(2, min(16, size // 4 or 2))}


def solve(payload: dict[str, Any]) -> dict[str, Any]:
    left = payload["left"]
    right = payload["right"]
    block_size = payload["block_size"]
    size = len(left)
    result = [[0 for _ in range(size)] for _ in range(size)]
    for row_block in range(0, size, block_size):
        for col_block in range(0, size, block_size):
            for inner_block in range(0, size, block_size):
                for i in range(row_block, min(row_block + block_size, size)):
                    left_row = left[i]
                    result_row = result[i]
                    for k in range(inner_block, min(inner_block + block_size, size)):
                        factor = left_row[k]
                        right_row = right[k]
                        for j in range(col_block, min(col_block + block_size, size)):
                            result_row[j] += factor * right_row[j]
    trace = sum(result[index][index] for index in range(size))
    checksum = sum(sum(row) for row in result)
    return {"size": size, "trace": trace, "checksum": checksum}


TASK_SPEC = TaskSpec("compute_core", generate, solve, 16, 64)
