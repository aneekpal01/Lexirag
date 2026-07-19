"""
Parses uploaded documents into page-level text so every chunk can be traced
back to a (document, page_number) pair for citation.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from pypdf import PdfReader
from docx import Document as DocxDocument


@dataclass
class PageText:
    page_number: int
    text: str


def parse_pdf(file_path: str) -> list[PageText]:
    reader = PdfReader(file_path)
    pages: list[PageText] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(PageText(page_number=i, text=text))
    return pages


def parse_docx(file_path: str) -> list[PageText]:
    # DOCX has no native page concept until rendered; we treat the whole
    # document as "page 1" and rely on paragraph offsets for finer citation
    # later. Good enough for v1.
    doc = DocxDocument(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [PageText(page_number=1, text=full_text)] if full_text.strip() else []


def parse_txt(file_path: str) -> list[PageText]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [PageText(page_number=1, text=text)] if text.strip() else []


def parse_image_ocr(file_path: str) -> list[PageText]:
    # Requires pytesseract + tesseract-ocr installed on the host.
    import pytesseract
    from PIL import Image

    text = pytesseract.image_to_string(Image.open(file_path))
    return [PageText(page_number=1, text=text)] if text.strip() else []


def parse_document(file_path: str) -> list[PageText]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    if ext == ".docx":
        return parse_docx(file_path)
    if ext == ".txt":
        return parse_txt(file_path)
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        return parse_image_ocr(file_path)
    raise ValueError(f"Unsupported file type: {ext}")
