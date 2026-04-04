# relational_fusion

What it does: Joins two relations and computes aggregate outputs.

Algorithm design:
- Build hash index on join key for one side.
- Stream the other side and perform hash join.
- Aggregate joined rows into summary values.

Why this design:
- Mirrors common database execution strategy.
- Efficient for large join-heavy workloads.

Input: Synthetic left/right relational rows.

Output: `left_rows`, `right_rows`, `join_rows`, `aggregate`, `checksum`.
