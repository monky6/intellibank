import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from backend.config import (
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    TOP_K_RETRIEVAL
)

class VectorStoreManager:
    def __init__(
        self,
        persist_dir: str = str(CHROMA_DIR),
        collection_name: str = CHROMA_COLLECTION_NAME,
        model_name: str = EMBEDDING_MODEL_NAME
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.model_name = model_name

        # Initialize Embedding Model
        print(f"Loading embedding model: {self.model_name}...")
        self.embedding_model = SentenceTransformer(self.model_name)

        # Initialize Persistent ChromaDB Client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"ChromaDB initialized at {self.persist_dir}. Current document chunks: {self.collection.count()}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates normalized vector embeddings for a list of texts."""
        embeddings = self.embedding_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Embeds and indexes document chunks in ChromaDB.
        Avoids duplicates by checking existing IDs.
        """
        if not chunks:
            return 0

        ids = [c["id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings(texts)

        # Batch upsert into Chroma
        batch_size = 64
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            self.collection.upsert(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=texts[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )

        return len(chunks)

    def search(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """
        Searches for top_k most semantically relevant chunks for a given query.
        Returns chunks with metadata, text, and normalized similarity score (0.0 to 1.0).
        """
        if self.collection.count() == 0:
            return []

        query_embedding = self.generate_embeddings([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        retrieved_chunks = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                # For cosine distance in Chroma: similarity = 1 - distance
                similarity_score = max(0.0, min(1.0, 1.0 - dist))
                retrieved_chunks.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity_score": round(float(similarity_score), 4),
                    "document_name": meta.get("document_name", "Unknown"),
                    "page_number": meta.get("page_number", 1)
                })

        return retrieved_chunks

    def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """
        Returns a summary of all indexed documents with their chunk and page counts.
        """
        count = self.collection.count()
        if count == 0:
            return []

        # Retrieve all metadatas to aggregate
        data = self.collection.get(include=["metadatas"])
        docs_summary: Dict[str, Dict[str, Any]] = {}

        for meta in data.get("metadatas", []):
            doc_name = meta.get("document_name", "Unknown")
            page_num = meta.get("page_number", 1)
            
            if doc_name not in docs_summary:
                docs_summary[doc_name] = {
                    "document_name": doc_name,
                    "chunk_count": 0,
                    "pages": set()
                }
            docs_summary[doc_name]["chunk_count"] += 1
            docs_summary[doc_name]["pages"].add(page_num)

        result = []
        for name, info in docs_summary.items():
            result.append({
                "document_name": name,
                "chunk_count": info["chunk_count"],
                "total_pages": len(info["pages"]),
                "pages_indexed": sorted(list(info["pages"]))
            })

        return sorted(result, key=lambda x: x["document_name"])

    def clear(self):
        """Resets the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
