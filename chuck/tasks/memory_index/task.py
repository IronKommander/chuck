from __future__ import annotations

from hashlib import blake2b, sha256
from random import Random
from typing import Any

from ...common import TaskSpec


def _bloom_hashes(value: str, bit_count: int, hash_count: int) -> list[int]:
    digest_a = int.from_bytes(blake2b(value.encode(), digest_size=8).digest(), "big")
    digest_b = int.from_bytes(sha256(value.encode()).digest()[:8], "big")
    return [((digest_a + index * digest_b) % bit_count) for index in range(hash_count)]


def generate(count: int, seed: int) -> dict[str, Any]:
    rng = Random(seed)
    items = [f"item_{seed}_{index}_{rng.randrange(10_000)}" for index in range(count)]
    probes = items[: count // 2]
    probes.extend(f"probe_{seed}_{index}_{rng.randrange(10_000)}" for index in range(count))
    return {"items": items, "probes": probes, "bit_count": max(256, count * 16), "hash_count": 4}


def solve(payload: dict[str, Any]) -> dict[str, Any]:
    items = payload["items"]
    probes = payload["probes"]
    bit_count = payload["bit_count"]
    hash_count = payload["hash_count"]
    bits = bytearray((bit_count + 7) // 8)

    def set_bit(position: int) -> None:
        bits[position // 8] |= 1 << (position % 8)

    def get_bit(position: int) -> bool:
        return bool(bits[position // 8] & (1 << (position % 8)))

    for item in items:
        for position in _bloom_hashes(item, bit_count, hash_count):
            set_bit(position)

    positives = 0
    true_positives = 0
    false_positives = 0
    item_set = set(items)
    for probe in probes:
        seen = all(get_bit(position) for position in _bloom_hashes(probe, bit_count, hash_count))
        if seen:
            positives += 1
            if probe in item_set:
                true_positives += 1
            else:
                false_positives += 1

    negative_count = max(1, len(probes) - len(items) // 2)
    false_positive_rate = false_positives / negative_count
    confidence = max(0.70, 1.0 - false_positive_rate)

    return {
        "items": len(items),
        "probes": len(probes),
        "positives": positives,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_positive_rate": round(false_positive_rate, 4),
        "probabilistic": True,
        "confidence": round(confidence, 4),
    }


TASK_SPEC = TaskSpec(
    "memory_index",
    generate,
    solve,
    128,
    10_000,
    algorithm_style="probabilistic",
    reliability_floor=0.85,
)
