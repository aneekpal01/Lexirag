"""
Single entry point for LLM calls so the rest of the app doesn't care whether
we're on Gemini or OpenAI. Switch via settings.llm_provider.
"""
from __future__ import annotations

from app.core.config import settings

SYSTEM_PROMPT = """You are LexiRAG, a legal research assistant. Answer ONLY using
the provided context chunks. Every factual claim must reference the chunk it
came from using [chunk_N]. If the context does not contain the answer, say so
explicitly instead of guessing. Never invent section numbers, page numbers, or
statute names."""


def _build_context_block(context_chunks: list[dict]) -> str:
    lines = []
    for i, c in enumerate(context_chunks, start=1):
        label = c.get("section_label") or "unlabeled section"
        lines.append(
            f"[chunk_{i}] (Document: {c['document_name']}, Page {c['page_number']}, {label})\n{c['text']}"
        )
    return "\n\n".join(lines)


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    context_block = _build_context_block(context_chunks)
    user_prompt = f"Context:\n{context_block}\n\nQuestion: {question}\n\nAnswer:"

    if settings.llm_provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            settings.llm_model, system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(user_prompt)
        return response.text

    if settings.llm_provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    raise ValueError(f"Unknown llm_provider: {settings.llm_provider}")
