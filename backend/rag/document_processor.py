"""
Document Processor
Processes PDF, TXT, and Markdown files for RAG pipeline
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import settings
from backend.rag.image_processor import image_processor
from backend.utils.logger import log


class DocumentProcessor:
    """
    Processes documents and splits them into chunks
    """
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        log.info(
            f"📄 DocumentProcessor initialized - "
            f"Chunk size: {self.chunk_size} | "
            f"Overlap: {self.chunk_overlap}"
        )
    
    def process_pdf(self, file_path: str, metadata: dict = None) -> List[Document]:
        """
        Process PDF file
        
        Args:
            file_path: Path to PDF file
            metadata: Additional metadata to attach
            
        Returns:
            List of Document chunks
        """
        try:
            log.info(f"📕 Processing PDF: {file_path}")
            
            # Load PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add custom metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split into chunks
            chunks = self._split_documents(
                documents,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            log.info(f"✅ PDF processed - {len(chunks)} chunks created")
            
            return chunks
            
        except Exception as e:
            log.error(f"❌ Error processing PDF: {str(e)}")
            raise
    
    def process_text(
        self,
        file_path: str,
        metadata: dict = None,
        file_type: str = "txt",
        process_images: bool = True
    ) -> List[Document]:
        """
        Process text file (TXT or MD)
        
        Args:
            file_path: Path to text file
            metadata: Additional metadata to attach
            file_type: File type (txt or md)
            process_images: If True, process image references for markdown files
            
        Returns:
            List of Document chunks
        """
        try:
            log.info(f"📝 Processing {file_type.upper()}: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document
            doc_metadata = {
                "source": file_path,
                "type": file_type,
                **(metadata or {})
            }
            
            document = Document(
                page_content=content,
                metadata=doc_metadata
            )
            
            # Choose separators based on file type
            if file_type == "md" or file_type == "markdown":
                separators = [
                    "\n## ",     # H2 headers
                    "\n### ",    # H3 headers
                    "\n#### ",   # H4 headers
                    "\n\n",      # Paragraphs
                    "\n",        # Lines
                    ". ",        # Sentences
                    " ",         # Words
                    ""
                ]
            else:
                separators = ["\n\n", "\n", ". ", " ", ""]
            
            # Split into chunks
            chunks = self._split_documents([document], separators=separators)
            
            # Process images for markdown files
            if (file_type in ["md", "markdown"]) and process_images:
                doc_dir = os.path.dirname(file_path)
                chunks = image_processor.process_document_with_images(
                    chunks,
                    doc_dir
                )
            
            log.info(f"✅ {file_type.upper()} processed - {len(chunks)} chunks created")
            
            return chunks
            
        except Exception as e:
            log.error(f"❌ Error processing text file: {str(e)}")
            raise
    
    def process_uploaded_file(
        self,
        file_content: bytes,
        filename: str,
        metadata: dict = None
    ) -> List[Document]:
        """
        Process uploaded file from bytes
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            metadata: Additional metadata
            
        Returns:
            List of Document chunks
        """
        # Determine file type
        extension = filename.split(".")[-1].lower()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{extension}"
        ) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            # Add filename to metadata
            file_metadata = {"filename": filename, **(metadata or {})}
            
            # Process based on file type
            if extension == "pdf":
                chunks = self.process_pdf(tmp_path, file_metadata)
            elif extension == "txt":
                chunks = self.process_text(tmp_path, file_metadata, "txt")
            elif extension in ["md", "markdown"]:
                chunks = self.process_text(tmp_path, file_metadata, "md")
            else:
                raise ValueError(f"Unsupported file type: {extension}")
            
            return chunks
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def _split_documents(
        self,
        documents: List[Document],
        separators: List[str] = None
    ) -> List[Document]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents
            separators: Custom separators for splitting
            
        Returns:
            List of chunked documents
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=separators or ["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        
        chunks = splitter.split_documents(documents)
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["chunk_id"] = f"chunk-{uuid4().hex[:12]}"
        
        return chunks
    
    def get_stats(self, chunks: List[Document]) -> dict:
        """
        Get statistics about processed chunks
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
            }
        
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_characters": sum(chunk_sizes),
            "avg_chunk_size": sum(chunk_sizes) // len(chunks),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
        }


# Singleton instance
document_processor = DocumentProcessor()

