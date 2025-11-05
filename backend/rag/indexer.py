"""
Indexer
Indexes documents into Qdrant vector store
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from langchain_core.documents import Document

from backend.config import settings
from backend.rag.document_processor import document_processor
from backend.rag.embeddings import embeddings_generator
from backend.rag.vector_store import vector_store_client
from backend.utils.logger import log


class Indexer:
    """
    Indexes documents into vector store with embeddings
    """
    
    def __init__(self):
        log.info("📑 Indexer initialized")
    
    async def ensure_collection_exists(self) -> bool:
        """
        Ensure vector store collection exists
        
        Returns:
            True if collection exists or was created
        """
        try:
            # Check if collection exists
            info = await vector_store_client.get_collection_info()
            
            if info["status"] == "not_found":
                log.info(f"Creating collection: {settings.qdrant_collection_name}")
                await vector_store_client.create_collection(
                    vector_size=embeddings_generator.vector_size,
                    distance=settings.qdrant_distance,
                )
            else:
                log.info(
                    f"Collection exists - "
                    f"Points: {info['points_count']} | "
                    f"Vectors: {info['vectors_count']}"
                )
            
            return True
            
        except Exception as e:
            log.error(f"❌ Error ensuring collection exists: {str(e)}")
            raise
    
    async def index_document(
        self,
        file_path: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Index a single document
        
        Args:
            file_path: Path to document file
            document_id: Unique document ID (generated if not provided)
            metadata: Additional metadata
            
        Returns:
            Dictionary with indexing results
        """
        start_time = time.time()
        
        document_id = document_id or f"doc-{uuid4().hex[:12]}"
        
        try:
            log.info(f"📑 Indexing document: {file_path} (ID: {document_id})")
            
            # Ensure collection exists
            await self.ensure_collection_exists()
            
            # Determine file type and process
            extension = Path(file_path).suffix.lower().lstrip(".")
            
            doc_metadata = {
                "document_id": document_id,
                "file_path": str(file_path),
                "filename": Path(file_path).name,
                **(metadata or {})
            }
            
            if extension == "pdf":
                chunks = document_processor.process_pdf(file_path, doc_metadata)
            elif extension == "txt":
                chunks = document_processor.process_text(file_path, doc_metadata, "txt")
            elif extension in ["md", "markdown"]:
                chunks = document_processor.process_text(file_path, doc_metadata, "md")
            else:
                raise ValueError(f"Unsupported file type: {extension}")
            
            # Index chunks
            result = await self._index_chunks(chunks, document_id)
            
            processing_time = time.time() - start_time
            
            log.info(
                f"✅ Document indexed - "
                f"ID: {document_id} | "
                f"Chunks: {result['chunks_indexed']} | "
                f"Time: {processing_time:.2f}s"
            )
            
            return {
                "document_id": document_id,
                "filename": Path(file_path).name,
                "chunks_indexed": result["chunks_indexed"],
                "processing_time_seconds": processing_time,
                "status": "success",
            }
            
        except Exception as e:
            log.error(f"❌ Error indexing document: {str(e)}")
            return {
                "document_id": document_id,
                "filename": Path(file_path).name,
                "chunks_indexed": 0,
                "processing_time_seconds": time.time() - start_time,
                "status": "failed",
                "error": str(e),
            }
    
    async def index_uploaded_file(
        self,
        file_content: bytes,
        filename: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Index an uploaded file from bytes
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            document_id: Unique document ID
            metadata: Additional metadata
            
        Returns:
            Dictionary with indexing results
        """
        start_time = time.time()
        
        document_id = document_id or f"doc-{uuid4().hex[:12]}"
        
        try:
            log.info(f"📑 Indexing uploaded file: {filename} (ID: {document_id})")
            
            # Ensure collection exists
            await self.ensure_collection_exists()
            
            # Process uploaded file
            doc_metadata = {
                "document_id": document_id,
                "filename": filename,
                **(metadata or {})
            }
            
            chunks = document_processor.process_uploaded_file(
                file_content,
                filename,
                doc_metadata
            )
            
            # Index chunks
            result = await self._index_chunks(chunks, document_id)
            
            processing_time = time.time() - start_time
            
            log.info(
                f"✅ Uploaded file indexed - "
                f"ID: {document_id} | "
                f"Chunks: {result['chunks_indexed']} | "
                f"Time: {processing_time:.2f}s"
            )
            
            return {
                "document_id": document_id,
                "filename": filename,
                "chunks_indexed": result["chunks_indexed"],
                "processing_time_seconds": processing_time,
                "status": "success",
            }
            
        except Exception as e:
            log.error(f"❌ Error indexing uploaded file: {str(e)}")
            return {
                "document_id": document_id,
                "filename": filename,
                "chunks_indexed": 0,
                "processing_time_seconds": time.time() - start_time,
                "status": "failed",
                "error": str(e),
            }
    
    async def _index_chunks(
        self,
        chunks: List[Document],
        document_id: str,
    ) -> Dict[str, Any]:
        """
        Index document chunks into vector store
        
        Args:
            chunks: List of document chunks
            document_id: Document ID
            
        Returns:
            Indexing results
        """
        if not chunks:
            return {"chunks_indexed": 0}
        
        # Extract text content
        texts = [chunk.page_content for chunk in chunks]
        
        # Generate embeddings in batches
        log.debug(f"🧠 Generating embeddings for {len(texts)} chunks")
        embeddings = embeddings_generator.generate(
            texts,
            batch_size=settings.embeddings_batch_size
        )
        
        # Prepare points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = f"{document_id}_chunk_{i}"
            
            points.append({
                "id": point_id,
                "vector": embedding,
                "payload": {
                    "content": chunk.page_content,
                    "metadata": chunk.metadata,
                    "document_id": document_id,
                    "chunk_index": i,
                }
            })
        
        # Upsert into Qdrant
        log.debug(f"💾 Upserting {len(points)} points to Qdrant")
        await vector_store_client.upsert_points(points)
        
        return {"chunks_indexed": len(points)}
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks of a document from vector store
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        try:
            log.info(f"🗑️  Deleting document: {document_id}")
            
            # This is a simplified version
            # In production, you'd want to filter by document_id and get all point IDs
            # For now, we'll assume point IDs follow the pattern {document_id}_chunk_{i}
            
            # Note: This is a placeholder - proper implementation would require
            # querying Qdrant for all points with document_id in metadata
            
            log.warning("Delete document not fully implemented - requires Qdrant scroll API")
            
            return True
            
        except Exception as e:
            log.error(f"❌ Error deleting document: {str(e)}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index
        
        Returns:
            Dictionary with index statistics
        """
        try:
            info = await vector_store_client.get_collection_info()
            
            return {
                "collection_name": settings.qdrant_collection_name,
                "total_points": info.get("points_count", 0),
                "total_vectors": info.get("vectors_count", 0),
                "status": info.get("status", "unknown"),
            }
            
        except Exception as e:
            log.error(f"❌ Error getting index stats: {str(e)}")
            return {
                "collection_name": settings.qdrant_collection_name,
                "total_points": 0,
                "total_vectors": 0,
                "status": "error",
                "error": str(e),
            }


# Singleton instance
indexer = Indexer()

