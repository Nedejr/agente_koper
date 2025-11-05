"""
Documents API
Endpoints for document management with RAG integration
"""

import time
from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.config import settings
from backend.models.document import (
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentProcessResponse,
    DocumentStats,
    DocumentStatus,
    DocumentType,
    DocumentUploadResponse,
)
from backend.rag.indexer import indexer
from backend.utils.logger import log

router = APIRouter()

# In-memory storage for document metadata (use Redis or DB in production)
documents_db: Dict[str, dict] = {}


def get_file_type(filename: str) -> DocumentType:
    """Determina o tipo do arquivo pela extensão"""
    extension = filename.split(".")[-1].lower()
    
    if extension == "pdf":
        return DocumentType.PDF
    elif extension == "txt":
        return DocumentType.TXT
    elif extension in ["md", "markdown"]:
        return DocumentType.MARKDOWN
    else:
        return DocumentType.OTHER


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process document",
    description="Upload a document and automatically process it for RAG"
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process document
    
    - Accepts PDF, TXT, MD
    - Validates file size
    - Automatically processes and indexes into vector store
    - Returns document ID
    """
    log.info(f"📤Upload started - File: {file.filename}")
    
    try:
        # Validate file type
        file_type = get_file_type(file.filename)
        if file_type == DocumentType.OTHER:
            extension = file.filename.split(".")[-1]
            if extension not in settings.allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type. Use: {', '.join(settings.allowed_extensions)}"
                )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum: {settings.max_file_size_mb}MB"
            )
        
        # Generate document ID
        document_id = f"doc-{uuid4().hex[:12]}"
        
        # Store document metadata
        documents_db[document_id] = {
            "document_id": document_id,
            "filename": file.filename,
            "file_size_bytes": file_size,
            "file_type": file_type.value,
            "status": DocumentStatus.PROCESSING,
            "upload_time": time.time(),
        }
        
        log.info(f"✅ Upload completed - ID: {document_id} | Size: {file_size} bytes")
        
        # Process and index document asynchronously
        try:
            result = await indexer.index_uploaded_file(
                file_content=content,
                filename=file.filename,
                document_id=document_id,
            )
            
            # Update status
            documents_db[document_id]["status"] = (
                DocumentStatus.COMPLETED if result["status"] == "success"
                else DocumentStatus.FAILED
            )
            documents_db[document_id]["chunks_count"] = result.get("chunks_indexed", 0)
            documents_db[document_id]["processing_time"] = result.get("processing_time_seconds", 0)
            
            if result["status"] != "success":
                documents_db[document_id]["error"] = result.get("error")
            
        except Exception as e:
            log.error(f"❌ Error processing document: {str(e)}")
            documents_db[document_id]["status"] = DocumentStatus.FAILED
            documents_db[document_id]["error"] = str(e)
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size_bytes=file_size,
            file_type=file_type,
            status=documents_db[document_id]["status"],
            message=f"Document uploaded and {'processed successfully' if documents_db[document_id]['status'] == DocumentStatus.COMPLETED else 'processing failed'}",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload error: {str(e)}"
        )


@router.post(
    "/documents/{document_id}/process",
    response_model=DocumentProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Processar documento",
    description="Processa um documento e gera embeddings"
)
async def process_document(document_id: str):
    """
    Processa documento
    
    - Divide em chunks
    - Gera embeddings
    - Armazena no Qdrant
    """
    log.info(f"⚙️  Processamento iniciado - Doc: {document_id}")
    
    start_time = time.time()
    
    try:
        # TODO: Implementar processamento real
        # Por enquanto, mock
        
        processing_time = time.time() - start_time
        
        log.info(f"✅ Processamento concluído - Doc: {document_id} | Tempo: {processing_time:.2f}s")
        
        return DocumentProcessResponse(
            document_id=document_id,
            filename="documento.pdf",
            status=DocumentStatus.COMPLETED,
            chunks_created=45,
            processing_time_seconds=processing_time,
            message="Documento processado com sucesso (mock)"
        )
        
    except Exception as e:
        log.error(f"❌ Erro no processamento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar documento: {str(e)}"
        )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List documents",
    description="List all indexed documents"
)
async def list_documents(page: int = 1, page_size: int = 50):
    """
    List all documents
    """
    from datetime import datetime
    from backend.models.document import DocumentInfo
    
    # Convert documents_db to list of DocumentInfo
    documents_list = []
    for doc_id, doc_data in documents_db.items():
        documents_list.append(DocumentInfo(
            document_id=doc_data["document_id"],
            filename=doc_data["filename"],
            file_type=DocumentType(doc_data["file_type"]),
            file_size_bytes=doc_data["file_size_bytes"],
            status=doc_data["status"],
            chunks_count=doc_data.get("chunks_count", 0),
            uploaded_at=datetime.fromtimestamp(doc_data["upload_time"]),
            processed_at=datetime.fromtimestamp(doc_data["upload_time"] + doc_data.get("processing_time", 0)) if doc_data.get("processing_time") else None,
            error=doc_data.get("error"),
        ))
    
    # Simple pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated = documents_list[start:end]
    
    return DocumentListResponse(
        documents=paginated,
        total=len(documents_list),
        page=page,
        page_size=page_size,
    )


@router.delete(
    "/documents/{document_id}",
    response_model=DocumentDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete document",
    description="Remove a document and its embeddings from vector store"
)
async def delete_document(document_id: str):
    """
    Delete document and its vectors
    """
    log.info(f"🗑️  Delete started - Doc: {document_id}")
    
    if document_id not in documents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    doc_data = documents_db[document_id]
    filename = doc_data["filename"]
    
    try:
        # Delete from vector store
        await indexer.delete_document(document_id)
        
        # Delete from metadata storage
        del documents_db[document_id]
        
        log.info(f"✅ Document deleted - ID: {document_id}")
        
        return DocumentDeleteResponse(
            document_id=document_id,
            filename=filename,
            message="Document and embeddings deleted successfully",
        )
        
    except Exception as e:
        log.error(f"❌ Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )


@router.get(
    "/documents/stats",
    response_model=DocumentStats,
    status_code=status.HTTP_200_OK,
    summary="Document statistics",
    description="Get statistics about indexed documents"
)
async def get_documents_stats():
    """
    Get document statistics
    """
    total_documents = len(documents_db)
    total_chunks = sum(doc.get("chunks_count", 0) for doc in documents_db.values())
    total_size_bytes = sum(doc.get("file_size_bytes", 0) for doc in documents_db.values())
    
    # Count by type
    documents_by_type = {}
    for doc in documents_db.values():
        file_type = doc.get("file_type", "unknown")
        documents_by_type[file_type] = documents_by_type.get(file_type, 0) + 1
    
    # Count by status
    documents_by_status = {}
    for doc in documents_db.values():
        status = doc.get("status", "unknown").value if hasattr(doc.get("status"), "value") else str(doc.get("status"))
        documents_by_status[status] = documents_by_status.get(status, 0) + 1
    
    # Get index stats from Qdrant
    index_stats = await indexer.get_index_stats()
    
    return DocumentStats(
        total_documents=total_documents,
        total_chunks=index_stats.get("total_points", total_chunks),
        total_size_bytes=total_size_bytes,
        documents_by_type=documents_by_type,
        documents_by_status=documents_by_status,
    )

