import os
import uuid

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.core.config import settings
from app.models.schemas import UploadResponse
from app.services import vectorstore
from app.services.chunker import chunk_pages
from app.services.document_parser import parse_document
from app.services.embeddings import embed_texts

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".webp"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile, workspace_id: str = Form(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    os.makedirs(settings.upload_dir, exist_ok=True)
    document_id = str(uuid.uuid4())
    saved_path = os.path.join(settings.upload_dir, f"{document_id}{ext}")

    contents = await file.read()
    if len(contents) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {settings.max_upload_mb}MB limit")
    with open(saved_path, "wb") as f:
        f.write(contents)

    pages = parse_document(saved_path)
    if not pages:
        raise HTTPException(422, "No extractable text found in document")

    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(422, "Document produced no chunks")

    vectors = embed_texts([c.text for c in chunks])

    vectorstore.upsert_chunks(
        document_id=document_id,
        document_name=file.filename,
        workspace_id=workspace_id,
        chunk_texts=[c.text for c in chunks],
        chunk_vectors=vectors,
        page_numbers=[c.page_number for c in chunks],
        section_labels=[c.section_label for c in chunks],
    )

    return UploadResponse(
        document_id=document_id,
        document_name=file.filename,
        pages_indexed=len(pages),
        chunks_indexed=len(chunks),
    )
