from __future__ import annotations

from random import Random
from typing import Any

from ...common import TaskSpec, round6


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


def solve(graph: dict[str, list[str]], iterations: int = 16, damping: float = 0.85) -> dict[str, Any]:
    nodes = sorted(graph)
    if not nodes:
        return {"node_count": 0, "top_node": "", "top_score": 0.0, "checksum": 0.0}

    rank = {node: 1.0 / len(nodes) for node in nodes}
    outgoing = {node: graph[node] if graph[node] else nodes for node in nodes}
    base = (1.0 - damping) / len(nodes)
    for _ in range(iterations):
        new_rank = {node: base for node in nodes}
        for node in nodes:
            share = rank[node] / len(outgoing[node])
            for target in outgoing[node]:
                new_rank[target] += damping * share
        rank = new_rank
    top_node = max(nodes, key=lambda node: (rank[node], node))
    checksum = sum((index + 1) * rank[node] for index, node in enumerate(nodes))
    return {
        "node_count": len(nodes),
        "top_node": top_node,
        "top_score": round6(rank[top_node]),
        "checksum": round6(checksum),
    }


TASK_SPEC = TaskSpec("graph_analytics", generate, solve, 48, 1_000)
