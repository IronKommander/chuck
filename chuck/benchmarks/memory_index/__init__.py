from __future__ import annotations

from typing import Any

from ...common import benchmark_task
from ...tasks.memory_index import TASK_SPEC


def run() -> dict[str, Any]:
    return benchmark_task(TASK_SPEC, seed=1_008)
