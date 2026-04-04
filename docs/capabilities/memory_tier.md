# memory_tier

What it does: Simulates cache behavior on hot/cold access streams.

Algorithm design:
- Process key accesses in order.
- Keep a bounded LRU-style cache.
- Track hits, misses, and final key state.

Why this design:
- Captures common memory-tier behavior with simple rules.
- Easy to reason about hit-rate changes.

Input: Mixed hot/cold key access sequence.

Output: `requests`, `hits`, `misses`, `hit_rate`, `final_keys`.
