# compute_core

What it does: Runs dense numeric kernels on generated matrices.

Algorithm design:
- Build deterministic square matrices.
- Run matrix-style multiply/accumulate loops.
- Read final trace and checksum.

Why this design:
- Represents CPU-heavy numeric workloads.
- Deterministic math makes regression checks stable.

Input: Generated square matrices.

Output: `size`, `trace`, `checksum`.
