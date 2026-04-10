# graph_analytics: Examples & Usage

This benchmark simulates a PageRank algorithm on a randomly generated directed graph.
- First, a directed graph with no isolated nodes is generated.
- Then, nodes are ranked based on how many other nodes are linked to it through exactly 16 iterations.
- Then, metadata like checksum is calculated and the `top_node` is identified.

## CLI Benchmark

The below command can be used to benchmark your system on this task:

```bash
python -m chuck bench --task graph_analytics
```
Output:
```text
Benchmark summary:
- graph_analytics: 0.018138s on size 1000 (node_count=1000)
```

## Usage in Code

If you want to use or modify this benchmark in your own code, you will need to import `TASK_SPEC` from `graph_analytics` and `solve_with_backend` function from the `native_bindings` file.

For example, this snippet displays the time taken along with JSON result data:
```python
from chuck.native_bindings import solve_with_backend
from chuck.tasks.graph_analytics import TASK_SPEC
import time

payload = TASK_SPEC.generator(10000, 117) # Number of nodes, and seed is 117
st_time = time.perf_counter()
result = solve_with_backend(task=TASK_SPEC, payload=payload, backend="python")
ed_time = time.perf_counter()
print(f"{result}, took time: {ed_time - st_time}")
```

Output:
```text
{'node_count': 10000, 'top_node': 'n9990', 'top_score': 0.000412, 'checksum': 5001.623833, 'backend': 'python'}, took time: 0.08808568000677042
```
