# memory_index

What it does: Runs fast membership checks using a Bloom-filter style index.

Algorithm design:
- Hash each inserted item to multiple bit positions.
- Set bits in a compact bit-array index.
- Probe membership and track false positives.

Why this design:
- Very memory-efficient lookup.
- Trades exactness for speed and compact storage.

Input: Inserted keys and probe keys.

Output: `items`, `queries`, `true_positives`, `false_positives`, `false_positive_rate`, `confidence`.
