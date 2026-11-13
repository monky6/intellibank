import os
import re
from typing import List, Dict, Any, Optional
from groq import Groq
from backend.config import (
    GROQ_API_KEY,
    DEFAULT_GROQ_MODEL,
    SYSTEM_PROMPT,
    TOP_K_RETRIEVAL
)
from backend.vector_store import VectorStoreManager

class RAGChain:
    def __init__(
        self,
        vector_store: VectorStoreManager,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_GROQ_MODEL
    ):
        self.vector_store = vector_store
        self.api_key = api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
        self.model_name = model_name
        self._groq_client = None

        if self.api_key:
            try:
                self._groq_client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Groq client: {e}")

    def update_api_key(self, new_key: str):
        """Allows dynamically updating or setting the Groq API key."""
        self.api_key = new_key.strip()
        if self.api_key:
            self._groq_client = Groq(api_key=self.api_key)
        else:
            self._groq_client = None

    def _is_out_of_scope(self, query: str) -> Optional[str]:
        """
        Heuristic safety guardrail to detect explicitly out-of-scope banking questions.
        """
        q_lower = query.lower()
        crypto_keywords = ["bitcoin", "crypto", "ethereum", "dogecoin", "token", "nft", "solana", "binance", "coinbase"]
        if any(w in q_lower for w in crypto_keywords):
            return (
                "**Policy Notice: Cryptocurrency & Virtual Assets Out of Scope**\n\n"
                "IntelliBank does not provide cryptocurrency brokerage, digital asset custody, "
                "or speculative token trading services. Per our official Wealth Management & "
                "Treasury disclosures (Doc: `Investment_and_Deposit_Services.pdf`, Page 1), "
                "inquiries regarding crypto transfers and digital currencies are strictly outside our operational scope.\n\n"
                "If you need assistance with traditional wealth management or FDIC-insured deposits, our advisors will be glad to assist."
            )
        
        tax_keywords = ["file my taxes", "tax deduction for my business", "how to avoid capital gains tax", "tax loophole"]
        if any(w in q_lower for w in tax_keywords):
            return (
                "**Notice: Tax & Legal Advice Limitation**\n\n"
                "IntelliBank policy materials and automated assistants do not provide personal tax or legal advice. "
                "Please consult a certified public accountant (CPA) or licensed tax attorney regarding personal or corporate tax filings."
            )

        return None

    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks into a clean prompt context block."""
        if not chunks:
            return "No relevant banking documents found in the knowledge base."

        formatted = []
        for i, chunk in enumerate(chunks, 1):
            doc = chunk.get("document_name", "Unknown Document")
            page = chunk.get("page_number", 1)
            score = chunk.get("similarity_score", 0.0)
            text = chunk.get("text", "").strip()
            formatted.append(f"--- [Source {i}: {doc} (Page {page}) | Match: {score*100:.1f}%] ---\n{text}")

        return "\n\n".join(formatted)

    def extract_citations(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts structured citations for the UI."""
        citations = []
        seen = set()

        for chunk in chunks:
            doc = chunk.get("document_name", "Unknown")
            page = chunk.get("page_number", 1)
            key = (doc, page)

            excerpt = chunk.get("text", "").strip()
            if len(excerpt) > 220:
                excerpt = excerpt[:220] + "..."

            citations.append({
                "document_name": doc,
                "page_number": page,
                "similarity_score": chunk.get("similarity_score", 0.0),
                "relevance_pct": round(chunk.get("similarity_score", 0.0) * 100, 1),
                "excerpt": excerpt
            })
            seen.add(key)

        return citations

    def generate_local_grounded_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Deterministic, offline fallback response synthesizer when no Groq key is present.
        Accurately synthesizes information from retrieved chunks with citations.
        """
        if not chunks or chunks[0].get("similarity_score", 0.0) < 0.25:
            return (
                "I am sorry, but that information is not available in our official IntelliBank policy documents.\n\n"
                "Please contact an IntelliBank branch representative or call our 24/7 customer service desk at "
                "**1-800-555-4683** for direct assistance.\n\n"
                "_Note: Running in Local Grounded Retrieval mode. Add a Groq API key in the sidebar for full Llama-3 generation._"
            )

        top_chunk = chunks[0]
        doc_name = top_chunk.get("document_name", "Document")
        page_num = top_chunk.get("page_number", 1)
        score_pct = top_chunk.get("similarity_score", 0.0) * 100

        # Build clean informative response
        response_parts = [
            f"According to official **IntelliBank** guidelines (`{doc_name}`, Page {page_num}):\n"
        ]

        # Extract sentences from chunks that best match query terms
        query_words = set(re.findall(r'\w+', query.lower()))
        extracted_facts = []

        for chunk in chunks[:3]:
            text = chunk.get("text", "")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines:
                if len(line) > 20 and any(w in line.lower() for w in query_words if len(w) > 3):
                    c_doc = chunk.get("document_name")
                    c_page = chunk.get("page_number")
                    fact_str = f"• {line} *[{c_doc} - Page {c_page}]*"
                    if fact_str not in extracted_facts:
                        extracted_facts.append(fact_str)

        if extracted_facts:
            response_parts.extend(extracted_facts[:5])
        else:
            # Fallback to presenting the top excerpt
            response_parts.append(f"> {top_chunk.get('text', '').strip()}\n")
            response_parts.append(f"\n*Source: [{doc_name} - Page {page_num}]*")

        response_parts.append("\n\n---\n*Disclaimer: Rates, terms, and policies are subject to regulatory updates and account approval.*")
        response_parts.append("\n*(Generated via Local Grounded Retrieval Engine. To enable real-time Groq Llama 3.3 generation, provide your GROQ_API_KEY in the sidebar settings.)*")

        return "\n".join(response_parts)

    def answer_question(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = TOP_K_RETRIEVAL
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline:
        1. Checks out-of-scope guardrail
        2. Retrieves top-k semantically relevant chunks from ChromaDB
        3. Checks retrieval confidence threshold
        4. Synthesizes grounded answer using Groq Llama 3.3 or local fallback
        5. Returns structured answer, citations, confidence, and metadata
        """
        query_clean = query.strip()
        if not query_clean:
            return {
                "answer": "Please ask a question regarding IntelliBank accounts, loans, credit cards, or policies.",
                "citations": [],
                "grounded": False,
                "confidence": 0.0,
                "model_used": "none"
            }

        # Step 1: Pre-retrieval Out-of-Scope Guardrail Check
        out_of_scope_msg = self._is_out_of_scope(query_clean)
        if out_of_scope_msg:
            return {
                "answer": out_of_scope_msg,
                "citations": [],
                "grounded": True,
                "confidence": 1.0,
                "model_used": "guardrail_policy"
            }

        # Step 2: Semantic Retrieval from Vector Store
        retrieved_chunks = self.vector_store.search(query=query_clean, top_k=top_k)

        # Confidence metric (similarity score of highest matching chunk)
        top_score = retrieved_chunks[0]["similarity_score"] if retrieved_chunks else 0.0
        citations = self.extract_citations(retrieved_chunks)

        # Step 3: Low-Relevance Guardrail Check (< 0.25 similarity implies no relevant bank policy exists)
        if not retrieved_chunks or top_score < 0.25:
            safe_refusal = (
                "I am sorry, but I could not find verified information regarding that in our official IntelliBank policy documents.\n\n"
                "To ensure strict accuracy and avoid incorrect financial information, I only provide answers based on official records. "
                "Please visit your nearest IntelliBank branch or reach our customer concierge at **1-800-555-4683**."
            )
            return {
                "answer": safe_refusal,
                "citations": citations[:1] if citations else [],
                "grounded": False,
                "confidence": round(top_score, 3),
                "model_used": "grounding_guardrail"
            }

        context_str = self.format_context(retrieved_chunks)

        # Step 4: LLM Generation (Groq Llama 3.3 or Local Grounded Fallback)
        if self._groq_client:
            try:
                # Build messages payload with conversation history
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]

                if chat_history:
                    # Append up to last 4 conversation turns for context
                    for msg in chat_history[-4:]:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        if role in ["user", "assistant"] and content:
                            messages.append({"role": role, "content": content})

                user_prompt = (
                    f"Official Banking Documents Context:\n"
                    f"{context_str}\n\n"
                    f"Customer Question: {query_clean}\n\n"
                    f"Instructions: Provide a clear, professional answer strictly grounded in the context above. "
                    f"Cite source documents and page numbers for specific figures or terms. If the answer is not in the context, decline politely."
                )
                messages.append({"role": "user", "content": user_prompt})

                completion = self._groq_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.1,  # Low temperature for deterministic factual recall
                    max_tokens=800
                )
                answer_text = completion.choices[0].message.content
                model_used = self.model_name

            except Exception as e:
                print(f"Groq API call error: {e}. Falling back to local grounded engine.")
                answer_text = self.generate_local_grounded_answer(query_clean, retrieved_chunks)
                model_used = "local_grounded_engine (Groq fallback)"
        else:
            answer_text = self.generate_local_grounded_answer(query_clean, retrieved_chunks)
            model_used = "local_grounded_engine"

        return {
            "answer": answer_text,
            "citations": citations,
            "grounded": True,
            "confidence": round(top_score, 3),
            "model_used": model_used
        }
