from __future__ import annotations

from collections import defaultdict
from random import Random
from typing import Any

from ...common import TaskSpec


def generate(count: int, seed: int) -> list[str]:
    rng = Random(seed)
    accounts = [f"acct_{i:03d}" for i in range(max(8, count // 8 or 8))]
    buckets = [f"bucket_{i:02d}" for i in range(max(4, count // 12 or 4))]
    records = []
    for _ in range(count):
        account = accounts[rng.randrange(len(accounts))]
        bucket = buckets[rng.randrange(len(buckets))]
        amount = rng.randrange(1, 1_000)
        records.append(f"{account}|{bucket}|{amount}")
    return records


def solve(records: list[str]) -> dict[str, Any]:
    totals: dict[str, int] = defaultdict(int)
    count = 0
    for line in records:
        account, bucket, amount_text = line.split("|")
        key = f"{account}|{bucket}"
        totals[key] += int(amount_text)
        count += 1
    top_pair, top_value = max(totals.items(), key=lambda item: (item[1], item[0]))
    return {
        "records": count,
        "unique_pairs": len(totals),
        "total_value": sum(totals.values()),
        "top_pair": top_pair,
        "top_value": top_value,
    }


TASK_SPEC = TaskSpec("io_pipeline", generate, solve, 64, 120_000)
