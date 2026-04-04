from __future__ import annotations

from hashlib import sha256
from random import Random
from typing import Any

from ...common import TaskSpec, round4


def generate(size: int, seed: int) -> bytes:
    rng = Random(seed)
    pattern = bytearray()
    alphabet = b"abcdefghijklmnopqrstuvwxyz0123456789"
    for index in range(size):
        pattern.append(alphabet[(rng.randrange(len(alphabet)) + index) % len(alphabet)])
        if index % 97 == 0:
            pattern.extend(f"|{seed}|".encode())
    return bytes(pattern[:size]) if size else b""


def solve(payload: bytes) -> dict[str, Any]:
    import zlib

    compressed = zlib.compress(payload, level=6)
    restored = zlib.decompress(compressed)
    digest = sha256(restored).hexdigest()
    ratio = len(compressed) / len(payload) if payload else 0.0
    return {
        "input_bytes": len(payload),
        "compressed_bytes": len(compressed),
        "ratio": round4(ratio),
        "roundtrip": restored == payload,
        "sha256": digest,
    }


TASK_SPEC = TaskSpec("data_encoding", generate, solve, 8_192, 2_000_000)
