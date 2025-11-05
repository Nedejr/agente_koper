"""
Documents API
Endpoints para gerenciamento de documentos
"""

import time
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
from backend.utils.logger import log

router = APIRouter()


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
    summary="Upload de documento",
    description="Faz upload de um documento para processamento"
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload de documento
    
    - Aceita PDF, TXT, MD
    - Valida tamanho máximo
    - Retorna ID do documento
    """
    log.info(f"📤 Upload iniciado - Arquivo: {file.filename}")
    
    try:
        # Valida tipo de arquivo
        file_type = get_file_type(file.filename)
        if file_type == DocumentType.OTHER:
            extension = file.filename.split(".")[-1]
            if extension not in settings.allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de arquivo não suportado. Use: {', '.join(settings.allowed_extensions)}"
                )
        
        # Lê conteúdo do arquivo
        content = await file.read()
        file_size = len(content)
        
        # Valida tamanho
        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Máximo: {settings.max_file_size_mb}MB"
            )
        
        # Gera ID do documento
        document_id = f"doc-{uuid4().hex[:12]}"
        
        # TODO: Salvar arquivo no sistema de arquivos
        # TODO: Adicionar à fila de processamento
        
        log.info(f"✅ Upload concluído - ID: {document_id} | Tamanho: {file_size} bytes")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size_bytes=file_size,
            file_type=file_type,
            status=DocumentStatus.PENDING,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Erro no upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload: {str(e)}"
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
    summary="Listar documentos",
    description="Lista todos os documentos"
)
async def list_documents(page: int = 1, page_size: int = 50):
    """
    Lista documentos
    """
    # TODO: Implementar listagem real
    return DocumentListResponse(
        documents=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.delete(
    "/documents/{document_id}",
    response_model=DocumentDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Deletar documento",
    description="Remove um documento e seus embeddings"
)
async def delete_document(document_id: str):
    """
    Deleta documento
    """
    log.info(f"🗑️  Remoção iniciada - Doc: {document_id}")
    
    # TODO: Implementar remoção real
    
    return DocumentDeleteResponse(
        document_id=document_id,
        filename="documento.pdf",
    )


@router.get(
    "/documents/stats",
    response_model=DocumentStats,
    status_code=status.HTTP_200_OK,
    summary="Estatísticas dos documentos",
    description="Retorna estatísticas gerais sobre os documentos"
)
async def get_documents_stats():
    """
    Estatísticas dos documentos
    """
    # TODO: Implementar estatísticas reais
    return DocumentStats(
        total_documents=0,
        total_chunks=0,
        total_size_bytes=0,
        documents_by_type={},
        documents_by_status={},
    )

