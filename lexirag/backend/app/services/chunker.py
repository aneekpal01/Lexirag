"""
Splits parsed pages into overlapping chunks sized for embedding, while
carrying forward the page number (and a best-guess section label) so
retrieval results can be cited precisely.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.config import settings
from app.services.document_parser import PageText

SECTION_PATTERN = re.compile(
    r"(Section\s+\d+[A-Za-z]?|Article\s+\d+|Clause\s+\d+(\.\d+)*)", re.IGNORECASE
)


@dataclass
class Chunk:
    text: str
    page_number: int
    section_label: str | None
    chunk_index: int


def _guess_section_label(text: str) -> str | None:
    match = SECTION_PATTERN.search(text)
    return match.group(0) if match else None


def chunk_pages(
    pages: list[PageText],
    chunk_size: int = settings.chunk_size,
    overlap: int = settings.chunk_overlap,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0
    for page in pages:
        words = page.text.split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            piece = " ".join(words[start:end])
            chunks.append(
                Chunk(
                    text=piece,
                    page_number=page.page_number,
                    section_label=_guess_section_label(piece),
                    chunk_index=idx,
                )
            )
            idx += 1
            if end == len(words):
                break
            start = end - overlap
    return chunks
