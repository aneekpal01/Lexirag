from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    document_name: str
    pages_indexed: int
    chunks_indexed: int


class ChatRequest(BaseModel):
    question: str
    workspace_id: str


class CitationOut(BaseModel):
    document_name: str
    page_number: int
    section_label: str | None
    confidence: float
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationOut]
