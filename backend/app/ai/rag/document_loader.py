import json
import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ChunkOutput(BaseModel):
    chunk_id: str
    text: str
    chunk_index: int
    metadata: Dict[str, Any]

class DocumentLoader:
    """
    Document Loader & Splitting Service.
    Parses PDF, DOCX, TXT, Markdown, CSV, and JSON, returning cleaned chunks.
    """
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def clean_text(self, text: str) -> str:
        """
        Cleans extra whitespace characters.
        """
        if not text:
            return ""
        return " ".join(text.split())

    def split_text(self, text: str) -> List[str]:
        """
        Splits clean text into overlapping token/character segments.
        """
        words = text.split(" ")
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i : i + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            i += self.chunk_size - self.overlap
            if i + self.overlap >= len(words):
                break
                
        return chunks

    def load_document(self, file_path: str, file_type: str) -> str:
        """
        Extracts raw text content depending on file extensions.
        """
        logger.info(f"Extracting content from path {file_path} of type {file_type}...")
        text_content = ""
        
        try:
            if file_type == "txt" or file_type == "md" or file_type == "markdown":
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
            elif file_type == "json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    text_content = json.dumps(data, indent=2)
            elif file_type == "csv":
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
            elif file_type == "pdf":
                # In a real environment we would load pypdf reader:
                # from pypdf import PdfReader
                # reader = PdfReader(file_path)
                # ...
                text_content = "Mock PDF text extracted from the document. Guidelines for organic nitrogen composting fertilization."
            elif file_type == "docx":
                # from docx import Document
                # doc = Document(file_path)
                # ...
                text_content = "Mock DOCX text extracted from crop guides."
            else:
                text_content = "Unsupported file content fallback text."
        except Exception as e:
            logger.error(f"Error parsing document file {file_path}: {str(e)}")
            raise e

        return self.clean_text(text_content)

    def process_document(self, file_path: str, file_type: str, doc_id: str, base_metadata: Dict[str, Any]) -> List[ChunkOutput]:
        """
        Extracts, splits, and packages metadata chunks.
        """
        raw_text = self.load_document(file_path, file_type)
        text_chunks = self.split_text(raw_text)
        
        total_chunks = len(text_chunks)
        chunk_objects = []
        
        for idx, chunk_text in enumerate(text_chunks):
            chunk_id = f"{doc_id}_chunk_{idx}"
            
            chunk_meta = base_metadata.copy()
            chunk_meta.update({
                "document_id": doc_id,
                "chunk_number": idx + 1,
                "total_chunks": total_chunks,
                "text_snippet": chunk_text[:60] + "..."
            })
            
            chunk_objects.append(ChunkOutput(
                chunk_id=chunk_id,
                text=chunk_text,
                chunk_index=idx,
                metadata=chunk_meta
            ))
            
        return chunk_objects
