# io_pipeline

What it does: Reads many line records, transforms them, and computes totals.

Algorithm design:
- Parse each record in one pass.
- Group by `(account, bucket)` and sum amounts.
- Track the top pair using a running max.

Why this design:
- Single-pass aggregation keeps memory and time predictable.
- Good fit for stream-like IO workloads.

Input: Line records shaped like `account|bucket|amount`.

Output: `records`, `groups`, `top_pair`, `top_value`, `checksum`.
