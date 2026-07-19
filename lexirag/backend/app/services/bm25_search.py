"""
Lightweight BM25 keyword search to complement vector search in the hybrid
retrieval step. For v1 this indexes chunks pulled from Postgres per-request;
swap for a persistent BM25/OpenSearch index once corpus size grows.
"""
from __future__ import annotations

from dataclasses import dataclass

from rank_bm25 import BM25Okapi


@dataclass
class BM25Result:
    chunk_id: str
    score: float


def build_index(chunk_ids: list[str], chunk_texts: list[str]) -> BM25Okapi:
    tokenized = [text.lower().split() for text in chunk_texts]
    return BM25Okapi(tokenized)


def search(
    query: str, chunk_ids: list[str], chunk_texts: list[str], top_k: int
) -> list[BM25Result]:
    if not chunk_ids:
        return []
    bm25 = build_index(chunk_ids, chunk_texts)
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(zip(chunk_ids, scores), key=lambda x: x[1], reverse=True)
    return [BM25Result(chunk_id=cid, score=score) for cid, score in ranked[:top_k]]
