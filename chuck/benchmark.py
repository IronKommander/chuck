from __future__ import annotations

from typing import Any

from .benchmarks import (
    run_compute_core,
    run_data_encoding,
    run_graph_analytics,
    run_io_pipeline,
    run_memory_index,
    run_memory_tier,
    run_ordering_core,
    run_prime_analytics,
    run_relational_fusion,
    run_retrieval_core,
)


RUNNERS = [
    run_io_pipeline,
    run_ordering_core,
    run_retrieval_core,
    run_data_encoding,
    run_graph_analytics,
    run_prime_analytics,
    run_memory_tier,
    run_memory_index,
    run_compute_core,
    run_relational_fusion,
]

RUNNER_BY_NAME = {
    "io_pipeline": run_io_pipeline,
    "ordering_core": run_ordering_core,
    "retrieval_core": run_retrieval_core,
    "data_encoding": run_data_encoding,
    "graph_analytics": run_graph_analytics,
    "prime_analytics": run_prime_analytics,
    "memory_tier": run_memory_tier,
    "memory_index": run_memory_index,
    "compute_core": run_compute_core,
    "relational_fusion": run_relational_fusion,
}


def run_benchmarks(task: str | None = None) -> list[dict[str, Any]]:
    if task is None:
        return [runner() for runner in RUNNERS]
    runner = RUNNER_BY_NAME[task]
    return [runner()]


def _compact_output(output: Any) -> str:
    if not isinstance(output, dict):
        return str(output)

    preferred_keys = [
        "records",
        "count",
        "doc_count",
        "input_bytes",
        "node_count",
        "candidates",
        "probable_primes",
        "jobs",
        "requests",
        "items",
        "size",
        "left_rows",
    ]
    parts = [f"{key}={output[key]}" for key in preferred_keys if key in output]
    if not parts:
        parts = [f"{key}={value}" for key, value in list(output.items())[:4]]
    return ", ".join(parts)


def format_benchmarks(results: list[dict[str, Any]]) -> str:
    lines = ["Benchmark summary:"]
    for result in results:
        lines.append(f"- {result['task']}: {result['seconds']}s on size {result['size']} ({_compact_output(result['output'])})")
    return "\n".join(lines)
