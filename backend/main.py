import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import (
    UPLOADS_DIR,
    SAMPLE_DOCS_DIR,
    DEFAULT_GROQ_MODEL
)
from backend.document_processor import DocumentProcessor
from backend.vector_store import VectorStoreManager
from backend.rag_chain import RAGChain

app = FastAPI(
    title="IntelliBank AI Banking Assistant API",
    description="Enterprise RAG Backend for Banking Policy Retrieval & Grounded Q&A",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Singletons
doc_processor = DocumentProcessor()
vector_store = VectorStoreManager()
rag_chain = RAGChain(vector_store=vector_store)

# Pydantic Schemas
class MessageItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's banking query")
    history: Optional[List[MessageItem]] = Field(default=[], description="Recent conversation turns")
    groq_api_key: Optional[str] = Field(default=None, description="Optional dynamic Groq API Key")
    model: Optional[str] = Field(default=DEFAULT_GROQ_MODEL, description="Groq model identifier")

class CitationItem(BaseModel):
    document_name: str
    page_number: int
    similarity_score: float
    relevance_pct: float
    excerpt: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem]
    grounded: bool
    confidence: float
    model_used: str

class DocumentSummary(BaseModel):
    document_name: str
    chunk_count: int
    total_pages: int
    pages_indexed: List[int]

class IndexStatusResponse(BaseModel):
    status: str
    chunks_indexed: int
    documents: List[DocumentSummary]
    total_vectors: int

@app.on_event("startup")
def startup_event():
    """On startup, automatically ingest sample banking documents if vector store is empty."""
    current_count = vector_store.collection.count()
    print(f"IntelliBank API starting up. Existing vectors in database: {current_count}")
    if current_count == 0 and SAMPLE_DOCS_DIR.exists():
        print("Knowledge base is empty. Automatically indexing official sample banking documents...")
        chunks = doc_processor.process_directory(str(SAMPLE_DOCS_DIR))
        if chunks:
            added = vector_store.add_chunks(chunks)
            print(f"Startup Ingestion complete: {added} chunks indexed from {SAMPLE_DOCS_DIR}.")

@app.get("/")
def read_root():
    return {
        "service": "IntelliBank AI Banking Assistant API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "chat": "POST /api/chat",
            "upload": "POST /api/upload",
            "documents": "GET /api/documents",
            "reset": "POST /api/reset",
            "index_sample_docs": "POST /api/index-sample-docs"
        }
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "vector_count": vector_store.collection.count(),
        "embedding_model": vector_store.model_name,
        "groq_configured": bool(rag_chain.api_key),
        "groq_model": rag_chain.model_name
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Update API key or model dynamically if passed in request
    if request.groq_api_key and request.groq_api_key != rag_chain.api_key:
        rag_chain.update_api_key(request.groq_api_key)
    if request.model:
        rag_chain.model_name = request.model

    history_dicts = [{"role": m.role, "content": m.content} for m in request.history] if request.history else []
    result = rag_chain.answer_question(query=request.query, chat_history=history_dicts)

    return ChatResponse(
        answer=result["answer"],
        citations=[CitationItem(**c) for c in result["citations"]],
        grounded=result["grounded"],
        confidence=result["confidence"],
        model_used=result["model_used"]
    )

@app.get("/api/documents", response_model=List[DocumentSummary])
def get_documents():
    docs = vector_store.get_indexed_documents()
    return [DocumentSummary(**d) for d in docs]

@app.post("/api/upload")
async def upload_pdf_documents(files: List[UploadFile] = File(...)):
    """Uploads one or more banking PDF documents, parses, chunks, and indexes them."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    saved_files = []
    total_new_chunks = 0

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue

        file_path = UPLOADS_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(str(file_path))

        # Process and index
        chunks = doc_processor.process_pdf(str(file_path))
        if chunks:
            count = vector_store.add_chunks(chunks)
            total_new_chunks += count

    return {
        "status": "success",
        "files_uploaded": len(saved_files),
        "chunks_indexed": total_new_chunks,
        "total_vectors": vector_store.collection.count()
    }

@app.post("/api/index-sample-docs", response_model=IndexStatusResponse)
def index_sample_documents():
    """Indexes the built-in sample banking documents."""
    if not SAMPLE_DOCS_DIR.exists():
        raise HTTPException(status_code=404, detail="sample_docs directory not found.")

    chunks = doc_processor.process_directory(str(SAMPLE_DOCS_DIR))
    added = vector_store.add_chunks(chunks)
    docs = vector_store.get_indexed_documents()

    return IndexStatusResponse(
        status="success",
        chunks_indexed=added,
        documents=[DocumentSummary(**d) for d in docs],
        total_vectors=vector_store.collection.count()
    )

@app.post("/api/reset")
def reset_database():
    """Clears all vectors and indexed documents."""
    vector_store.clear()
    return {
        "status": "success",
        "message": "Vector store successfully reset.",
        "vector_count": vector_store.collection.count()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
