# graph_analytics

What it does: Runs iterative scoring on a generated graph.

Algorithm design:
- Build adjacency lists.
- Run repeated neighbor-score propagation.
- Select top-scored node and compute checksum.

Why this design:
- Models iterative graph workloads (ranking/influence style).
- Deterministic updates make runs stable and comparable.

Input: Graph edges and node metadata.

Output: `node_count`, `edge_count`, `top_node`, `top_score`, `checksum`.
