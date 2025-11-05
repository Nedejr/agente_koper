"""
Modelos Pydantic para Documentos
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Tipos de documentos suportados"""
    PDF = "pdf"
    TXT = "txt"
    MARKDOWN = "md"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Status do processamento do documento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Metadados de um documento"""
    filename: str
    file_type: DocumentType
    file_size_bytes: int
    file_path: Optional[str] = None
    source: Optional[str] = None  # origem do documento
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentChunk(BaseModel):
    """Chunk de um documento após processamento"""
    chunk_id: str
    content: str
    metadata: dict = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    page_number: Optional[int] = None
    chunk_index: int


class DocumentUploadResponse(BaseModel):
    """Response após upload de documento"""
    document_id: str
    filename: str
    file_size_bytes: int
    file_type: DocumentType
    status: DocumentStatus = DocumentStatus.PENDING
    message: str = "Documento recebido e aguardando processamento"
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc-123456",
                "filename": "manual_koper.pdf",
                "file_size_bytes": 1048576,
                "file_type": "pdf",
                "status": "pending",
                "message": "Documento recebido e aguardando processamento",
                "uploaded_at": "2024-01-01T12:00:00"
            }
        }


class DocumentProcessResponse(BaseModel):
    """Response após processamento de documento"""
    document_id: str
    filename: str
    status: DocumentStatus
    chunks_created: int
    processing_time_seconds: float
    message: str
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc-123456",
                "filename": "manual_koper.pdf",
                "status": "completed",
                "chunks_created": 45,
                "processing_time_seconds": 12.5,
                "message": "Documento processado com sucesso"
            }
        }


class DocumentInfo(BaseModel):
    """Informações de um documento"""
    document_id: str
    filename: str
    file_type: DocumentType
    file_size_bytes: int
    status: DocumentStatus
    chunks_count: int = 0
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Lista de documentos"""
    documents: List[DocumentInfo]
    total: int
    page: int = 1
    page_size: int = 50
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "document_id": "doc-123456",
                        "filename": "manual_koper.pdf",
                        "file_type": "pdf",
                        "file_size_bytes": 1048576,
                        "status": "completed",
                        "chunks_count": 45,
                        "uploaded_at": "2024-01-01T12:00:00",
                        "processed_at": "2024-01-01T12:01:00"
                    }
                ],
                "total": 10,
                "page": 1,
                "page_size": 50
            }
        }


class DocumentDeleteResponse(BaseModel):
    """Response após deleção de documento"""
    document_id: str
    filename: str
    message: str = "Documento removido com sucesso"
    deleted_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentStats(BaseModel):
    """Estatísticas dos documentos"""
    total_documents: int
    total_chunks: int
    total_size_bytes: int
    documents_by_type: dict = Field(default_factory=dict)
    documents_by_status: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_documents": 10,
                "total_chunks": 450,
                "total_size_bytes": 10485760,
                "documents_by_type": {
                    "pdf": 7,
                    "txt": 2,
                    "md": 1
                },
                "documents_by_status": {
                    "completed": 9,
                    "processing": 1
                }
            }
        }

