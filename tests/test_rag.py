import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import SAMPLE_DOCS_DIR
from backend.document_processor import DocumentProcessor
from backend.vector_store import VectorStoreManager
from backend.rag_chain import RAGChain

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_tests():
    print("=" * 60)
    print("RUNNING INTELLIBANK AUTOMATED VERIFICATION SUITE")
    print("=" * 60)

    # 1. Test Document Processor
    print("\n[Test 1] Testing Document Processing with PyPDF...")
    processor = DocumentProcessor(chunk_size=600, chunk_overlap=100)
    chunks = processor.process_directory(str(SAMPLE_DOCS_DIR))
    assert len(chunks) > 0, "No chunks generated from sample_docs!"
    print(f"  [PASS] Extracted {len(chunks)} chunks across sample documents.")
    
    first_chunk = chunks[0]
    assert "document_name" in first_chunk["metadata"]
    assert "page_number" in first_chunk["metadata"]
    assert first_chunk["metadata"]["page_number"] >= 1
    print(f"  [PASS] Chunk metadata verified: {first_chunk['metadata']['document_name']} (Page {first_chunk['metadata']['page_number']})")

    # 2. Test Vector Store & Embeddings
    print("\n[Test 2] Testing Vector Indexing & Semantic Search...")
    test_db_dir = PROJECT_ROOT / "data" / "test_chroma_db"
    vector_store = VectorStoreManager(persist_dir=str(test_db_dir), collection_name="test_collection")
    vector_store.clear()
    
    added_count = vector_store.add_chunks(chunks)
    assert added_count == len(chunks)
    print(f"  [PASS] Successfully indexed {added_count} vectors into test ChromaDB.")

    # 3. Test Retrieval Precision - Overdraft Policy
    print("\n[Test 3] Testing Retrieval on Overdraft Policy...")
    results = vector_store.search("What is the fee for an overdraft and what time is the grace period?", top_k=2)
    assert len(results) > 0
    top_doc = results[0]["document_name"]
    top_score = results[0]["similarity_score"]
    assert "Personal_Banking_Policies_and_Fees" in top_doc
    assert top_score > 0.4
    print(f"  [PASS] Retrieved from: {top_doc} | Similarity: {top_score*100:.1f}%")
    assert "$35" in results[0]["text"] or "8:00 PM" in results[0]["text"]
    print(f"  [PASS] Verified policy details matched in retrieved passage.")

    # 4. Test Retrieval Precision - Mortgage Guidelines
    print("\n[Test 4] Testing Retrieval on Mortgage Terms...")
    results_mortgage = vector_store.search("30-year fixed conforming mortgage rate and minimum credit score", top_k=2)
    assert len(results_mortgage) > 0
    top_mortgage_doc = results_mortgage[0]["document_name"]
    assert "Home_and_Auto_Loan_Guidelines" in top_mortgage_doc
    print(f"  [PASS] Retrieved from: {top_mortgage_doc} | Similarity: {results_mortgage[0]['similarity_score']*100:.1f}%")

    # 5. Test RAG Chain & Guardrails
    print("\n[Test 5] Testing RAG Chain & Safety Guardrails...")
    rag = RAGChain(vector_store=vector_store)

    # Query A: Grounded Banking Question
    res_a = rag.answer_question("What is the penalty for early withdrawal on a 12-month CD?")
    assert res_a["grounded"] is True
    assert len(res_a["citations"]) > 0
    print(f"  [PASS] Grounded Answer returned with {len(res_a['citations'])} source citation(s).")
    print(f"    Confidence: {res_a['confidence']*100:.1f}%")

    # Query B: Out of Scope Cryptocurrency Inquiry
    res_b = rag.answer_question("How can I purchase Bitcoin using my bank account?")
    assert "Cryptocurrency & Virtual Assets Out of Scope" in res_b["answer"]
    assert res_b["model_used"] == "guardrail_policy"
    print(f"  [PASS] Crypto inquiry safely rejected by operational guardrail.")

    # Query C: Complete Hallucination / Unrelated Query
    res_c = rag.answer_question("What is the recipe for chocolate chip cookies on Jupiter?")
    assert res_c["grounded"] is False
    assert "not available in our official IntelliBank policy documents" in res_c["answer"] or "could not find verified information" in res_c["answer"]
    print(f"  [PASS] Unrelated query refused safely without hallucination.")

    # Clean up test DB
    vector_store.clear()
    print("\n" + "=" * 60)
    print("ALL 5 AUTOMATED TESTS PASSED SUCCESSFULLY! (100% PASS RATE)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
