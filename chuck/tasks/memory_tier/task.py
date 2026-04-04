from __future__ import annotations

from collections import OrderedDict
from random import Random
from typing import Any

from ...common import TaskSpec, round4


def generate(count: int, seed: int) -> dict[str, Any]:
    rng = Random(seed)
    hot_keys = [rng.randrange(max(16, count // 8 or 16)) for _ in range(8)]
    accesses = []
    for index in range(count):
        if index % 3 == 0:
            accesses.append(hot_keys[index % len(hot_keys)])
        else:
            accesses.append(rng.randrange(max(32, count // 4 or 32)))
    return {"capacity": max(8, count // 10 or 8), "accesses": accesses}


def solve(payload: dict[str, Any]) -> dict[str, Any]:
    capacity = payload["capacity"]
    accesses = payload["accesses"]
    cache: OrderedDict[int, int] = OrderedDict()
    hits = 0
    misses = 0
    for key in accesses:
        if key in cache:
            hits += 1
            cache.move_to_end(key)
        else:
            misses += 1
            cache[key] = key * key
            if len(cache) > capacity:
                cache.popitem(last=False)
    return {
        "requests": len(accesses),
        "hits": hits,
        "misses": misses,
        "hit_rate": round4(hits / len(accesses) if accesses else 0.0),
        "final_keys": list(cache.keys()),
    }


TASK_SPEC = TaskSpec("memory_tier", generate, solve, 128, 200_000)
