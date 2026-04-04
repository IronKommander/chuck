from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from chuck import regression
from chuck.regression import DEFAULT_REGRESSION_PATH, generate_regression_file, run_regression
from chuck.tasks import TASKS


class RegressionTests(unittest.TestCase):
    def test_task_count(self) -> None:
        self.assertEqual(len(TASKS), 10)

    def test_folder_layout(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        task_names = [
            "io_pipeline",
            "ordering_core",
            "retrieval_core",
            "data_encoding",
            "graph_analytics",
            "prime_analytics",
            "memory_tier",
            "memory_index",
            "compute_core",
            "relational_fusion",
        ]
        for task_name in task_names:
            self.assertTrue((repo_root / "chuck" / "tasks" / task_name).exists())
            self.assertTrue((repo_root / "chuck" / "benchmarks" / task_name).exists())

    def test_baseline_generation_and_match(self) -> None:
        original_dir = regression.DEFAULT_REGRESSION_DIR
        original_path = regression.DEFAULT_REGRESSION_PATH
        try:
            repo_root = Path(__file__).resolve().parents[1]
            with tempfile.TemporaryDirectory(dir=repo_root) as temp_dir:
                temp_root = Path(temp_dir)
                regression.DEFAULT_REGRESSION_DIR = temp_root
                regression.DEFAULT_REGRESSION_PATH = temp_root / "regression.json"
                path = generate_regression_file(regression.DEFAULT_REGRESSION_PATH)
                self.assertTrue(path.exists())
                manifest_root = Path(path).resolve().parents[1]

                entries = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(len(entries), 10)

                for entry in entries:
                    self.assertTrue((manifest_root / entry["path"]).exists())

                results = run_regression(path)
                self.assertTrue(all(result["passed"] for result in results))
        finally:
            regression.DEFAULT_REGRESSION_DIR = original_dir
            regression.DEFAULT_REGRESSION_PATH = original_path


if __name__ == "__main__":
    unittest.main()
