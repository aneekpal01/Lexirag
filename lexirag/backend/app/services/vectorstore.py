"""
Thin wrapper around Qdrant for document chunk storage + retrieval.
Each point payload carries everything needed to build a citation:
document_id, document_name, page_number, section_label, chunk_text.
"""
from __future__ import annotations

import uuid
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import settings


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection() -> None:
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=qmodels.VectorParams(
                size=settings.embedding_dim, distance=qmodels.Distance.COSINE
            ),
        )


def upsert_chunks(
    document_id: str,
    document_name: str,
    workspace_id: str,
    chunk_texts: list[str],
    chunk_vectors: list[list[float]],
    page_numbers: list[int],
    section_labels: list[str | None],
) -> None:
    ensure_collection()
    client = get_client()
    points = [
        qmodels.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "document_id": document_id,
                "document_name": document_name,
                "workspace_id": workspace_id,
                "page_number": page_numbers[i],
                "section_label": section_labels[i],
                "text": chunk_texts[i],
            },
        )
        for i, vector in enumerate(chunk_vectors)
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)


def scroll_workspace_chunks(
    workspace_id: str, limit: int = 5000
) -> tuple[list[str], list[str]]:
    """Fetch all (chunk_id, text) pairs for a workspace, used to build the
    BM25 corpus at query time. Fine for small/medium corpora; move to a
    persistent inverted index once a workspace has 10k+ chunks."""
    client = get_client()
    ids: list[str] = []
    texts: list[str] = []
    next_offset = None
    while True:
        points, next_offset = client.scroll(
            collection_name=settings.qdrant_collection,
            scroll_filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="workspace_id", match=qmodels.MatchValue(value=workspace_id)
                    )
                ]
            ),
            limit=min(500, limit - len(ids)),
            offset=next_offset,
            with_payload=True,
        )
        for p in points:
            ids.append(str(p.id))
            texts.append((p.payload or {}).get("text", ""))
        if next_offset is None or len(ids) >= limit:
            break
    return ids, texts


def vector_search(
    query_vector: list[float], workspace_id: str, top_k: int
) -> list[qmodels.ScoredPoint]:
    client = get_client()
    return client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        query_filter=qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="workspace_id", match=qmodels.MatchValue(value=workspace_id)
                )
            ]
        ),
        limit=top_k,
    )
