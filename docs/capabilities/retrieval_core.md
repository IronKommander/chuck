# retrieval_core

What it does: Builds a text index and answers query hit estimates quickly.

Algorithm design:
- Tokenize documents into terms.
- Build an inverted index from term to document list.
- Use sampled posting inspection for fast hit estimation.

Why this design:
- Indexing is deterministic, but sampled lookup trades some precision for speed.
- Useful for high-throughput retrieval scenarios.

Input: Synthetic documents and query terms.

Output: `doc_count`, `index_terms`, `query_hits`, `confidence`, `checksum`.
