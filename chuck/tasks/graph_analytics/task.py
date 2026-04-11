from __future__ import annotations

from random import Random
from typing import Any

from ...common import TaskSpec, round6
import numpy as np


def generate(node_count: int, seed: int) -> dict[str, list[str]]:
    rng = Random(seed)
    nodes = [f"n{index:04d}" for index in range(node_count)]
    graph: dict[str, list[str]] = {}
    for index, node in enumerate(nodes):
        degree = 2 + rng.randrange(3)
        edges = {nodes[(index + 1) % node_count]}
        while len(edges) < degree:
            edges.add(nodes[rng.randrange(node_count)])
        graph[node] = sorted(edges)
    return graph


def solve(graph: dict[str, list[str]] , iterations: int = 16, damping: float = 0.85) -> dict[str, Any]:
    if not graph:
        return {"node_count": 0, "top_node": "", "top_score": 0.0, "checksum": 0.0}

    nodes = sorted(graph)
    N = len(nodes)
    idx_map = {node: i for i, node in enumerate(nodes)}

    rows = np.array([idx_map[src] for src, targets in graph.items() for _ in targets], dtype=np.int64)
    cols = np.array([idx_map[tgt] for _, targets in graph.items() for tgt in targets], dtype=np.int64)
    out_degree = np.bincount(rows, minlength=N).astype(np.float64)

    rank = np.full((N,), 1.0/N, dtype=np.float64)
    base = (1.0 - damping) / N
    trans_wt = damping / out_degree

    for _ in range(iterations):
        msgs = (rank * trans_wt)[rows]
        recieved = np.bincount(cols, weights=msgs, minlength=N)
        rank = recieved + base

    top_node = int(np.argmax(rank))
    mult = np.arange(1, N+1)
    checksum = float(np.dot(mult, rank))

    return {
        "node_count": N,
        "top_node": f"n{top_node:04d}",
        "top_score": round6(float(rank[top_node])),
        "checksum" : round6(checksum),
    }


TASK_SPEC = TaskSpec("graph_analytics", generate, solve, 48, 1_000)
