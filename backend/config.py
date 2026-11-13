import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"
UPLOADS_DIR = DATA_DIR / "uploads"
SAMPLE_DOCS_DIR = PROJECT_ROOT / "sample_docs"

# Ensure directories exist
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Model & RAG Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
FALLBACK_GROQ_MODEL = "llama-3.1-8b-instant"

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHROMA_COLLECTION_NAME = "intellibank_knowledge_base"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
TOP_K_RETRIEVAL = 4

# Banking Guardrails Prompt
SYSTEM_PROMPT = """You are IntelliBank's AI-Powered Banking Assistant, an expert financial concierge.
Your mission is to provide accurate, helpful, and professional answers based EXCLUSIVELY on official IntelliBank policies, terms, disclosures, and guidelines provided in the context below.

CRITICAL OPERATIONAL RULES:
1. STRICT GROUNDING: Answer using ONLY the facts explicitly provided in the retrieved Context. Do NOT invent interest rates, fee amounts, deadlines, or terms.
2. CITATIONS: Whenever stating specific facts, amounts, rates, or rules, cite the source document and page number in parentheses, e.g. [Personal_Banking_Policies_and_Fees.pdf - Page 1].
3. OUT OF SCOPE / UNKNOWN HANDLING:
   - If the user asks a question whose answer is NOT present or verified in the provided Context, explicitly state:
     "I am sorry, but that information is not available in our official IntelliBank policy documents. Please contact an IntelliBank branch representative or call customer service at 1-800-555-4683 for assistance."
   - If the user asks about unauthorized topics (such as speculative crypto trading, tax advice, third-party unvetted loans, or personal non-banking advice), politely decline and state IntelliBank's policy boundary.
4. TONE & COURTESY: Maintain a polite, trustworthy, and compliant banking tone at all times. Format answers with clear bullet points where applicable.
5. FINANCIAL DISCLAIMER: When discussing loans, APY rates, or investments, include a brief standard disclosure: "Rates and terms are subject to change and underwriting approval."
"""
