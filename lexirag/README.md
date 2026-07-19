# LexiRAG AI — MVP

Legal document Q&A with cited answers. Scoped-down v1 of the full LexiRAG
vision: upload → hybrid RAG (vector + BM25) → answer with page/section
citations.

## What's in this MVP (and what's deliberately cut for v1)

**Included:**
- Multi-document upload: PDF, DOCX, TXT, image (OCR)
- Chunking with page + section tracking
- BGE-M3 embeddings → Qdrant vector store
- Hybrid retrieval: vector search + BM25, fused with reciprocal rank fusion
- Legal Q&A with citations (document, page, section, confidence score)
- Gemini 2.5 Flash / GPT-4.1 pluggable LLM backend

**Cut for v1** (build once the core loop is validated with real users):
- Clause extraction, contract comparison, risk detection
- AI drafting (NDA, employment agreement, etc.)
- PDF highlight-on-click, voice search, AI timeline
- Team workspace / RBAC beyond a single workspace_id
- Cohere rerank (RRF fusion is a reasonable stand-in for now)
- Auth (Clerk/Auth.js) — not wired up yet, add before any real deployment

## Stack

- Frontend: Next.js 15, TypeScript, Tailwind CSS
- Backend: FastAPI, Python 3.11
- Vector DB: Qdrant
- Embeddings: BGE-M3 (sentence-transformers)
- LLM: Gemini 2.5 Flash (default) or OpenAI GPT-4.1
- Infra: Docker Compose (Postgres, Redis, Qdrant)

## Running locally

1. Copy env template and add your LLM API key:
   ```bash
   cp backend/.env.example backend/.env
   # edit backend/.env — set GEMINI_API_KEY or OPENAI_API_KEY
   ```

2. Start everything:
   ```bash
   docker compose up --build
   ```

3. Open:
   - Frontend: http://localhost:3000
   - Backend docs: http://localhost:8000/docs

## Project structure

```
lexirag/
├── backend/
│   ├── app/
│   │   ├── core/config.py          # env-driven settings
│   │   ├── services/
│   │   │   ├── document_parser.py  # PDF/DOCX/TXT/OCR -> page text
│   │   │   ├── chunker.py          # page text -> cited chunks
│   │   │   ├── embeddings.py       # BGE-M3 embedding
│   │   │   ├── vectorstore.py      # Qdrant upsert/search
│   │   │   ├── bm25_search.py      # keyword search
│   │   │   ├── llm.py              # Gemini/OpenAI answer generation
│   │   │   └── rag_pipeline.py     # orchestrates the full RAG flow
│   │   ├── routers/upload.py       # POST /documents/upload
│   │   ├── routers/chat.py         # POST /chat
│   │   └── models/schemas.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx                # landing
│   │   ├── upload/page.tsx         # document upload
│   │   └── chat/page.tsx           # Q&A with citations
│   └── Dockerfile
└── docker-compose.yml
```

## Known gaps to fix before showing this to anyone outside your team

- No auth on the API — `workspace_id` is currently just a string anyone can pass
- BM25 rebuilds its index from a full Qdrant scroll on every query — fine
  under a few thousand chunks per workspace, will need a real inverted
  index (or Qdrant's built-in sparse vectors) past that
- No test suite yet
- No rate limiting
- Citation confidence is derived from raw cosine similarity, not a
  calibrated score — treat it as a relative signal, not a probability

## Next steps, in priority order

1. Add Clerk auth + real workspace scoping
2. Test retrieval quality against a real legal corpus (accuracy is the
   entire value prop here — don't skip this)
3. Add citation verification step (LLM re-checks its own citations against
   the source chunk before returning)
4. Then, and only then, start layering v2 features (clause extraction,
   contract comparison, risk detection)
