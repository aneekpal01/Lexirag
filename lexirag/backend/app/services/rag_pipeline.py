"""
Orchestrates the retrieval-augmented answer flow:

  question -> embed query -> vector search (Qdrant)
                           -> BM25 search (keyword)
           -> merge + dedupe -> (optional) Cohere rerank
           -> build cited context -> LLM -> answer + citations

Kept as plain functions (not LangGraph) for v1 so the flow is easy to trace
and debug. Once we add multi-step agent behavior (query rewriting, citation
verification, multi-hop reasoning) this is where LangGraph nodes plug in.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.services import bm25_search, llm, vectorstore
from app.services.embeddings import embed_query


@dataclass
class Citation:
    document_name: str
    page_number: int
    section_label: str | None
    confidence: float
    excerpt: str


@dataclass
class RAGAnswer:
    answer: str
    citations: list[Citation]


def _reciprocal_rank_fusion(
    vector_ranked: list[str], bm25_ranked: list[str], k: int = 60
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for rank, cid in enumerate(vector_ranked):
        scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
    for rank, cid in enumerate(bm25_ranked):
        scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
    return scores


def answer_question(
    question: str,
    workspace_id: str,
    corpus_chunk_ids: list[str],
    corpus_chunk_texts: list[str],
) -> RAGAnswer:
    # 1. Vector search
    query_vector = embed_query(question)
    vector_hits = vectorstore.vector_search(
        query_vector, workspace_id, top_k=settings.top_k_retrieve
    )
    vector_ranked_ids = [str(hit.id) for hit in vector_hits]
    vector_by_id = {str(hit.id): hit for hit in vector_hits}

    # 2. BM25 keyword search over the same candidate pool (v1: same corpus
    #    passed in by caller; swap for a real inverted index at scale)
    bm25_hits = bm25_search.search(
        question, corpus_chunk_ids, corpus_chunk_texts, top_k=settings.top_k_retrieve
    )
    bm25_ranked_ids = [h.chunk_id for h in bm25_hits]

    # 3. Fuse rankings
    fused = _reciprocal_rank_fusion(vector_ranked_ids, bm25_ranked_ids)
    top_ids = sorted(fused, key=fused.get, reverse=True)[: settings.top_k_final]

    # 4. Build context chunks (payload comes from vector hit if present)
    context_chunks = []
    for cid in top_ids:
        hit = vector_by_id.get(cid)
        if hit is None:
            continue
        payload = hit.payload or {}
        context_chunks.append(
            {
                "document_name": payload.get("document_name", "Unknown"),
                "page_number": payload.get("page_number", 0),
                "section_label": payload.get("section_label"),
                "text": payload.get("text", ""),
                "score": hit.score,
            }
        )

    if not context_chunks:
        return RAGAnswer(
            answer="I couldn't find anything relevant to this question in the uploaded documents.",
            citations=[],
        )

    # 5. Generate answer grounded in context
    answer_text = llm.generate_answer(question, context_chunks)

    # 6. Build citation list (confidence = normalized similarity score)
    citations = [
        Citation(
            document_name=c["document_name"],
            page_number=c["page_number"],
            section_label=c["section_label"],
            confidence=round(min(c["score"], 1.0) * 100, 1),
            excerpt=c["text"][:280],
        )
        for c in context_chunks
    ]

    return RAGAnswer(answer=answer_text, citations=citations)
