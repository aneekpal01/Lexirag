from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, CitationOut
from app.services import vectorstore
from app.services.rag_pipeline import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    chunk_ids, chunk_texts = vectorstore.scroll_workspace_chunks(req.workspace_id)

    result = answer_question(
        question=req.question,
        workspace_id=req.workspace_id,
        corpus_chunk_ids=chunk_ids,
        corpus_chunk_texts=chunk_texts,
    )

    return ChatResponse(
        answer=result.answer,
        citations=[
            CitationOut(
                document_name=c.document_name,
                page_number=c.page_number,
                section_label=c.section_label,
                confidence=c.confidence,
                excerpt=c.excerpt,
            )
            for c in result.citations
        ],
    )
