from __future__ import annotations

from random import Random
from typing import Any

from ...common import TaskSpec, round4


def _is_probable_prime(number: int, rounds: int = 5) -> bool:
    if number < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
    for prime in small_primes:
        if number == prime:
            return True
        if number % prime == 0:
            return False

    d = number - 1
    shifts = 0
    while d % 2 == 0:
        shifts += 1
        d //= 2

    rng = Random(number)
    for _ in range(rounds):
        a = rng.randrange(2, number - 1)
        x = pow(a, d, number)
        if x in (1, number - 1):
            continue
        witness_found = True
        for _ in range(shifts - 1):
            x = pow(x, 2, number)
            if x == number - 1:
                witness_found = False
                break
        if witness_found:
            return False
    return True


def generate(count: int, seed: int) -> list[int]:
    rng = Random(seed)
    start = 10**6 + seed * 7
    candidates = []
    for _ in range(count):
        value = start + rng.randrange(0, 2_000_000)
        if value % 2 == 0:
            value += 1
        candidates.append(value)
    return candidates


def solve(candidates: list[int]) -> dict[str, Any]:
    probable_primes = [n for n in candidates if _is_probable_prime(n, rounds=4)]
    checksum = sum(probable_primes) % 1_000_000_007
    confidence = 1.0 - (0.25 ** 4)
    return {
        "candidates": len(candidates),
        "probable_primes": len(probable_primes),
        "prime_density_estimate": round4(len(probable_primes) / len(candidates) if candidates else 0.0),
        "checksum": checksum,
        "probabilistic": True,
        "confidence": round4(confidence),
    }


TASK_SPEC = TaskSpec(
    "prime_analytics",
    generate,
    solve,
    128,
    100_000,
    algorithm_style="probabilistic",
    reliability_floor=0.90,
)
