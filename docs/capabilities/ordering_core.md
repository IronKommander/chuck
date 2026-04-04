# ordering_core

What it does: Sorts large integer batches and computes summary statistics.

Algorithm design:
- Sort each chunk.
- Merge sorted chunks into one ordered stream.
- Read order statistics (min/median/max) and compute checksum.

Why this design:
- Mirrors real data-engine sort + merge pipelines.
- Deterministic output is easy to regression-test.

Input: Integer arrays split into chunks.

Output: `count`, `min`, `median`, `max`, `checksum`.
