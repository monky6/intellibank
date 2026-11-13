import os
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "; ", " ", ""],
            length_function=len
        )

    def extract_text_by_pages(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Reads a PDF file page by page using PyPDF and returns a list of page dicts.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        reader = PdfReader(str(path))
        pages_content = []
        doc_name = path.name

        for page_idx, page in enumerate(reader.pages):
            page_number = page_idx + 1
            text = page.extract_text() or ""
            # Clean up excessive blank lines
            cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            if cleaned_text:
                pages_content.append({
                    "document_name": doc_name,
                    "page_number": page_number,
                    "text": cleaned_text
                })
        return pages_content

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts and splits a PDF into structured chunks with rich metadata.
        """
        pages_data = self.extract_text_by_pages(pdf_path)
        all_chunks = []

        for page in pages_data:
            doc_name = page["document_name"]
            page_num = page["page_number"]
            page_text = page["text"]

            # Split page text into chunks
            raw_chunks = self.text_splitter.split_text(page_text)

            for chunk_idx, chunk_text in enumerate(raw_chunks):
                chunk_id = f"{doc_name}_p{page_num}_c{chunk_idx+1}"
                all_chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        "document_name": doc_name,
                        "page_number": int(page_num),
                        "chunk_index": int(chunk_idx + 1),
                        "char_count": len(chunk_text)
                    }
                })

        return all_chunks

    def process_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """
        Processes all PDF files in a given directory.
        """
        directory = Path(dir_path)
        if not directory.exists():
            return []

        all_chunks = []
        for pdf_file in directory.glob("*.pdf"):
            chunks = self.process_pdf(str(pdf_file))
            all_chunks.extend(chunks)

        return all_chunks
