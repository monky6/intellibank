import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.main import app

def test_api():
    with TestClient(app) as client:
        print("Testing API Root...")
        r0 = client.get("/")
        assert r0.status_code == 200
        print(f"  [PASS] Root endpoint response: {r0.json()['service']}")

        print("Indexing official sample documents via API...")
        r_index = client.post("/api/index-sample-docs")
        assert r_index.status_code == 200
        print(f"  [PASS] Indexed {r_index.json()['chunks_indexed']} chunks.")

        print("Testing Health Endpoint...")
        r1 = client.get("/api/health")
        assert r1.status_code == 200
        health = r1.json()
        assert health["status"] == "healthy"
        assert health["vector_count"] > 0
        print(f"  [PASS] Health check OK. Vectors: {health['vector_count']}")

        print("Testing Documents Endpoint...")
        r2 = client.get("/api/documents")
        assert r2.status_code == 200
        docs = r2.json()
        assert len(docs) > 0
        print(f"  [PASS] Documents indexed: {len(docs)} documents.")

        print("Testing Chat Endpoint...")
        r3 = client.post("/api/chat", json={
            "query": "What is the fee for an overdraft and grace period?",
            "history": []
        })
        assert r3.status_code == 200
        data = r3.json()
        assert data["grounded"] is True
        assert len(data["citations"]) > 0
        print(f"  [PASS] Chat response received. Grounded: {data['grounded']} | Citations: {len(data['citations'])}")
        print(f"  Excerpt: {data['answer'][:120]}...")

        print("\n[ALL REST API ENDPOINT TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    test_api()
