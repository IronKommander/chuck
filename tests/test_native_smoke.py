from __future__ import annotations

import importlib.util
import unittest

from chuck.native_bindings import solve_with_backend
from chuck.tasks.compute_core import TASK_SPEC as COMPUTE_CORE_TASK
from chuck.tasks.data_encoding import TASK_SPEC as DATA_ENCODING_TASK
from chuck.tasks.graph_analytics import TASK_SPEC as GRAPH_ANALYTICS_TASK
from chuck.tasks.io_pipeline import TASK_SPEC as IO_PIPELINE_TASK
from chuck.tasks.memory_index import TASK_SPEC as MEMORY_INDEX_TASK
from chuck.tasks.memory_tier import TASK_SPEC as MEMORY_TIER_TASK
from chuck.tasks.ordering_core import TASK_SPEC as ORDERING_CORE_TASK
from chuck.tasks.prime_analytics import TASK_SPEC as PRIME_ANALYTICS_TASK
from chuck.tasks.relational_fusion import TASK_SPEC as RELATIONAL_FUSION_TASK
from chuck.tasks.retrieval_core import TASK_SPEC as RETRIEVAL_CORE_TASK


def _cpp_module_exists() -> bool:
    modules = [
        "chuck_cpp_prime_analytics",
        "chuck_cpp_memory_index",
        "chuck_cpp_ordering_core",
        "chuck_cpp_retrieval_core",
        "chuck_cpp_compute_core",
        "chuck_cpp_graph_analytics",
        "chuck_cpp_io_pipeline",
        "chuck_cpp_data_encoding",
        "chuck_cpp_memory_tier",
        "chuck_cpp_relational_fusion",
    ]
    return any(importlib.util.find_spec(name) is not None for name in modules)


@unittest.skipUnless(_cpp_module_exists(), "C++ native modules not installed")
class NativeSmokeTests(unittest.TestCase):
    def test_prime_analytics_cpp_backend(self) -> None:
        payload = PRIME_ANALYTICS_TASK.generator(PRIME_ANALYTICS_TASK.regression_size, seed=77)
        result = solve_with_backend(task=PRIME_ANALYTICS_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("probable_primes", result)

    def test_memory_index_cpp_backend(self) -> None:
        payload = MEMORY_INDEX_TASK.generator(MEMORY_INDEX_TASK.regression_size, seed=88)
        result = solve_with_backend(task=MEMORY_INDEX_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("false_positive_rate", result)

    def test_ordering_core_cpp_backend(self) -> None:
        payload = ORDERING_CORE_TASK.generator(ORDERING_CORE_TASK.regression_size, seed=99)
        result = solve_with_backend(task=ORDERING_CORE_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("checksum", result)

    def test_retrieval_core_cpp_backend(self) -> None:
        payload = RETRIEVAL_CORE_TASK.generator(RETRIEVAL_CORE_TASK.regression_size, seed=66)
        result = solve_with_backend(task=RETRIEVAL_CORE_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("query_hits", result)

    def test_compute_core_cpp_backend(self) -> None:
        payload = COMPUTE_CORE_TASK.generator(COMPUTE_CORE_TASK.regression_size, seed=55)
        result = solve_with_backend(task=COMPUTE_CORE_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("trace", result)

    def test_graph_analytics_cpp_backend(self) -> None:
        payload = GRAPH_ANALYTICS_TASK.generator(GRAPH_ANALYTICS_TASK.regression_size, seed=44)
        result = solve_with_backend(task=GRAPH_ANALYTICS_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("top_score", result)

    def test_io_pipeline_cpp_backend(self) -> None:
        payload = IO_PIPELINE_TASK.generator(IO_PIPELINE_TASK.regression_size, seed=12)
        result = solve_with_backend(task=IO_PIPELINE_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("top_pair", result)

    def test_data_encoding_cpp_backend(self) -> None:
        payload = DATA_ENCODING_TASK.generator(DATA_ENCODING_TASK.regression_size, seed=12)
        result = solve_with_backend(task=DATA_ENCODING_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("sha256", result)

    def test_memory_tier_cpp_backend(self) -> None:
        payload = MEMORY_TIER_TASK.generator(MEMORY_TIER_TASK.regression_size, seed=12)
        result = solve_with_backend(task=MEMORY_TIER_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("hit_rate", result)

    def test_relational_fusion_cpp_backend(self) -> None:
        payload = RELATIONAL_FUSION_TASK.generator(RELATIONAL_FUSION_TASK.regression_size, seed=12)
        result = solve_with_backend(task=RELATIONAL_FUSION_TASK, payload=payload, backend="cpp")
        self.assertEqual(result.get("backend"), "cpp")
        self.assertIn("join_rows", result)


if __name__ == "__main__":
    unittest.main()
