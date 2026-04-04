from __future__ import annotations

from collections import defaultdict
from random import Random
from typing import Any

from ...common import TaskSpec


def generate(count: int, seed: int) -> dict[str, Any]:
    rng = Random(seed)
    vocab = [
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
        "lambda",
        "mu",
    ]
    docs = []
    for doc_index in range(count):
        words = [vocab[(doc_index + offset + rng.randrange(4)) % len(vocab)] for offset in range(12)]
        docs.append(" ".join(words))
    queries = [vocab[(seed + index * 3) % len(vocab)] for index in range(5)]
    return {"docs": docs, "queries": queries}


def solve(payload: dict[str, Any]) -> dict[str, Any]:
    docs = payload["docs"]
    queries = payload["queries"]
    sample_stride = 2
    sampled_doc_ids = list(range(0, len(docs), sample_stride))
    sampled_docs = [docs[index] for index in sampled_doc_ids]

    index: dict[str, set[int]] = defaultdict(set)
    for doc_id, doc in zip(sampled_doc_ids, sampled_docs):
        for term in doc.split():
            index[term].add(doc_id)

    scale_factor = len(docs) / len(sampled_docs) if sampled_docs else 1.0
    top_term = ""
    top_size = -1
    for term, postings in index.items():
        posting_size = int(len(postings) * scale_factor)
        if posting_size > top_size or (posting_size == top_size and term < top_term):
            top_term = term
            top_size = posting_size
    query_hits = {query: int(len(index.get(query, set())) * scale_factor) for query in queries}

    coverage = len(sampled_docs) / len(docs) if docs else 1.0
    confidence = max(0.75, min(0.99, 0.65 + coverage * 0.45))
    return {
        "doc_count": len(docs),
        "sampled_docs": len(sampled_docs),
        "vocab_size": len(index),
        "top_term": top_term,
        "top_term_docs": top_size,
        "query_hits": query_hits,
        "probabilistic": True,
        "confidence": round(confidence, 4),
    }


TASK_SPEC = TaskSpec(
    "retrieval_core",
    generate,
    solve,
    48,
    2_000,
    algorithm_style="probabilistic",
    reliability_floor=0.88,
)
