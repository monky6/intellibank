import os
import sys
from pathlib import Path
import streamlit as st
import requests

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import (
    DEFAULT_GROQ_MODEL,
    FALLBACK_GROQ_MODEL,
    SAMPLE_DOCS_DIR
)
from backend.document_processor import DocumentProcessor
from backend.vector_store import VectorStoreManager
from backend.rag_chain import RAGChain

# Page Configuration
st.set_page_config(
    page_title="IntelliBank | AI Banking Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    /* Main Theme */
    .main {
        background-color: #F8FAFC;
    }
    .bank-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #1E40AF 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    .bank-header h1 {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .bank-header p {
        color: #93C5FD;
        margin: 8px 0 0 0;
        font-size: 14.5px;
    }
    .badge-grounded {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #86EFAC;
        display: inline-block;
        margin-bottom: 8px;
    }
    .badge-guardrail {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #FCD34D;
        display: inline-block;
        margin-bottom: 8px;
    }
    .citation-card {
        background: #FFFFFF;
        border-left: 4px solid #2563EB;
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-size: 13px;
        color: #334155;
    }
    .citation-meta {
        font-weight: 600;
        color: #1E40AF;
        margin-bottom: 4px;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State Singletons
@st.cache_resource(show_spinner="Initializing IntelliBank AI Engine & Vector DB...")
def get_backend_services():
    doc_proc = DocumentProcessor()
    v_store = VectorStoreManager()
    
    # Auto-index sample docs if empty
    if v_store.collection.count() == 0 and SAMPLE_DOCS_DIR.exists():
        chunks = doc_proc.process_directory(str(SAMPLE_DOCS_DIR))
        if chunks:
            v_store.add_chunks(chunks)

    chain = RAGChain(vector_store=v_store)
    return doc_proc, v_store, chain

doc_processor, vector_store, rag_chain = get_backend_services()

# Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 **Welcome to IntelliBank!** I am your AI Banking Assistant.\n\n"
                "I can answer your questions regarding our official banking accounts, overdraft rules, "
                "mortgage & auto loans, credit card protections, and investment rates with grounded source citations.\n\n"
                "How may I assist you with your banking needs today?"
            ),
            "citations": [],
            "grounded": True,
            "confidence": 1.0,
            "model_used": "system"
        }
    ]

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### ⚙️ Bank Configuration")
    
    # Groq API Key Input
    api_key_input = st.text_input(
        "Groq API Key (Optional)",
        type="password",
        value=rag_chain.api_key or "",
        help="Get a free high-speed API key at https://console.groq.com. If left blank, offline grounded search mode is used."
    )
    if api_key_input != rag_chain.api_key:
        rag_chain.update_api_key(api_key_input)
        if api_key_input:
            st.success("✅ Groq API Key updated!")

    # Model Selection
    selected_model = st.selectbox(
        "LLM Reasoning Model",
        options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-70b-8192"],
        index=0
    )
    rag_chain.model_name = selected_model

    st.divider()

    # Knowledge Base Stats
    st.markdown("### 📚 Knowledge Base")
    doc_count = vector_store.collection.count()
    st.metric("Total Indexed Chunks", doc_count)

    # Document Uploader
    st.markdown("#### Upload Official Documents")
    uploaded_files = st.file_uploader(
        "Add Banking PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload official fee schedules, disclosures, or product guides."
    )
    
    if uploaded_files:
        if st.button("Index Uploaded PDFs", type="primary", use_container_width=True):
            with st.spinner("Processing & embedding PDFs..."):
                saved_chunks = 0
                for uf in uploaded_files:
                    save_path = PROJECT_ROOT / "data" / "uploads" / uf.name
                    with open(save_path, "wb") as f:
                        f.write(uf.getbuffer())
                    chunks = doc_processor.process_pdf(str(save_path))
                    if chunks:
                        saved_chunks += vector_store.add_chunks(chunks)
                st.success(f"Indexed {saved_chunks} new chunks into ChromaDB!")
                st.rerun()

    # Re-index Built-in Sample Documents
    if st.button("🔄 Reload Official Sample Policies", use_container_width=True):
        with st.spinner("Re-indexing official bank policies..."):
            chunks = doc_processor.process_directory(str(SAMPLE_DOCS_DIR))
            added = vector_store.add_chunks(chunks)
            st.success(f"Successfully indexed {added} policy chunks.")
            st.rerun()

    # Document Library View
    with st.expander("📄 View Active Policy Documents", expanded=False):
        docs_summary = vector_store.get_indexed_documents()
        if docs_summary:
            for d in docs_summary:
                st.markdown(f"**{d['document_name']}**")
                st.caption(f"Pages: {d['total_pages']} | Chunks: {d['chunk_count']}")
        else:
            st.info("No documents indexed yet.")

    st.divider()

    # Clear Chat History
    if st.button("🗑️ Clear Chat Session", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ----------------- MAIN UI -----------------
st.markdown("""
<div class="bank-header">
    <h1>🏦 IntelliBank AI Assistant</h1>
    <p>Official Banking Information & Grounded Policy Concierge • Powered by Groq Llama-3 & Sentence Transformers</p>
</div>
""", unsafe_allow_html=True)

# Sample Query Pills
st.markdown("**💡 Common Banking Inquiries:**")
c1, c2, c3, c4, c5 = st.columns(5)

sample_q = None
if c1.button("💳 Overdraft Fees & Grace Period"):
    sample_q = "What is the overdraft fee and grace period for checking accounts?"
if c2.button("🏠 Mortgage Rates & Credit Score"):
    sample_q = "What are the 30-year fixed mortgage rates and minimum credit score required?"
if c3.button("🛡️ Credit Card Fraud Liability"):
    sample_q = "How does the zero liability credit card fraud protection work?"
if c4.button("📈 12-Month CD Early Withdrawal"):
    sample_q = "What is the APY rate and early withdrawal penalty on a 12-month CD?"
if c5.button("🚫 Crypto Trading Inquiry"):
    sample_q = "Can I buy Bitcoin or trade cryptocurrencies with my IntelliBank account?"

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Show Grounding Badge
        if msg["role"] == "assistant" and msg.get("model_used") != "system":
            if msg.get("grounded"):
                st.markdown(
                    f'<span class="badge-grounded">🛡️ Grounded in Bank Policy (Confidence: {int(msg.get("confidence", 0)*100)}%)</span>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<span class="badge-guardrail">⚠️ Outside Knowledge Base / Guardrail Active</span>',
                    unsafe_allow_html=True
                )

        st.markdown(msg["content"])

        # Display Source Citations
        citations = msg.get("citations", [])
        if citations:
            with st.expander(f"📑 Verified Source Citations ({len(citations)} references)", expanded=False):
                for idx, cit in enumerate(citations, 1):
                    st.markdown(
                        f"""
                        <div class="citation-card">
                            <div class="citation-meta">Source {idx}: {cit['document_name']} — Page {cit['page_number']} (Relevance: {cit['relevance_pct']}%)</div>
                            <div>"{cit['excerpt']}"</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# Handle User Input
user_input = st.chat_input("Ask about banking accounts, loan eligibility, card terms, or fees...") or sample_q

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant answer
    with st.chat_message("assistant"):
        with st.spinner("Searching official policies and generating grounded response..."):
            history_payload = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
                if m.get("model_used") != "system"
            ]
            response = rag_chain.answer_question(
                query=user_input,
                chat_history=history_payload
            )

            # Grounding Badge
            if response["grounded"]:
                st.markdown(
                    f'<span class="badge-grounded">🛡️ Grounded in Bank Policy (Confidence: {int(response["confidence"]*100)}%)</span>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<span class="badge-guardrail">⚠️ Outside Knowledge Base / Guardrail Active</span>',
                    unsafe_allow_html=True
                )

            st.markdown(response["answer"])

            # Citations
            if response["citations"]:
                with st.expander(f"📑 Verified Source Citations ({len(response['citations'])} references)", expanded=True):
                    for idx, cit in enumerate(response["citations"], 1):
                        st.markdown(
                            f"""
                            <div class="citation-card">
                                <div class="citation-meta">Source {idx}: {cit['document_name']} — Page {cit['page_number']} (Relevance: {cit['relevance_pct']}%)</div>
                                <div>"{cit['excerpt']}"</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # Store in session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "citations": response["citations"],
                "grounded": response["grounded"],
                "confidence": response["confidence"],
                "model_used": response["model_used"]
            })
