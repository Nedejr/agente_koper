"""
Backend API usando FastAPI
Esta é uma implementação alternativa que separa backend e frontend via HTTP

Para usar:
1. Instale: pip install fastapi uvicorn[standard] python-multipart
2. Execute: uvicorn backend_api.app:app --host 0.0.0.0 --port 8000
"""

import os

# Imports do backend
import sys
import tempfile
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.config import Config
from backend.processing import get_document_stats, process_pdf_file
from backend.qa import ask_question
from backend.vector_store import (
    add_to_vector_store,
    delete_vector_store,
    get_vector_store_stats,
    load_existing_vector_store,
)


# Modelos Pydantic para validação
class AskRequest(BaseModel):
    query: str
    model: Optional[str] = Config.DEFAULT_MODEL
    temperature: Optional[float] = Config.TEMPERATURE
    history: Optional[List[dict]] = None


class AskResponse(BaseModel):
    answer: str
    model: str


class UploadResponse(BaseModel):
    status: str
    files_processed: int
    total_chunks: int
    stats: dict


class StatsResponse(BaseModel):
    exists: bool
    total_documents: int
    persist_directory: str


# Inicializa FastAPI
app = FastAPI(
    title="Agente Koper API",
    description="API REST para sistema RAG com documentos PDF",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vector store global (carregado na inicialização)
vector_store = None


@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    global vector_store
    try:
        Config.validate()
        vector_store = load_existing_vector_store()
        print(f"✅ API iniciada. Vector store carregado: {vector_store is not None}")
    except Exception as e:
        print(f"⚠️ Erro na inicialização: {e}")


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Agente Koper API",
        "version": "1.0.0",
        "endpoints": {
            "POST /upload": "Upload de arquivos PDF",
            "POST /ask": "Fazer perguntas",
            "GET /stats": "Estatísticas do vector store",
            "DELETE /reset": "Resetar database",
        },
    }


@app.get("/health")
async def health_check():
    """Verifica saúde da API"""
    return {"status": "healthy", "vector_store_loaded": vector_store is not None}


@app.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload e processamento de documentos PDF

    Args:
        files: Lista de arquivos PDF

    Returns:
        Informações sobre o processamento
    """
    global vector_store

    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")

    try:
        all_chunks = []

        # Processa cada arquivo
        for file in files:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(
                    status_code=400, detail=f"Arquivo {file.filename} não é PDF"
                )

            # Salva temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            # Processa
            try:
                from io import BytesIO

                chunks = process_pdf_file(BytesIO(content))
                all_chunks.extend(chunks)
            finally:
                os.remove(tmp_path)

        # Obtém estatísticas
        stats = get_document_stats(all_chunks)

        # Adiciona ao vector store
        vector_store = add_to_vector_store(all_chunks, vector_store)

        return UploadResponse(
            status="success",
            files_processed=len(files),
            total_chunks=len(all_chunks),
            stats=stats,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Faz uma pergunta ao sistema RAG

    Args:
        request: Objeto com query, model, temperature e history

    Returns:
        Resposta gerada pelo modelo
    """
    global vector_store

    if not vector_store:
        raise HTTPException(
            status_code=400, detail="Nenhum documento carregado. Faça upload primeiro."
        )

    try:
        answer = ask_question(
            query=request.query,
            vector_store=vector_store,
            model_name=request.model,
            chat_history=request.history,
            temperature=request.temperature,
        )

        return AskResponse(answer=answer, model=request.model)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Retorna estatísticas do vector store

    Returns:
        Estatísticas do database
    """
    global vector_store

    stats = get_vector_store_stats(vector_store)

    return StatsResponse(
        exists=stats["exists"],
        total_documents=stats.get("total_documents", 0),
        persist_directory=stats.get("persist_directory", Config.PERSIST_DIR),
    )


@app.delete("/reset")
async def reset():
    """
    Reseta o vector store (remove todos os documentos)

    Returns:
        Mensagem de confirmação
    """
    global vector_store

    try:
        delete_vector_store()
        vector_store = None
        return {"status": "success", "message": "Vector store resetado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao resetar: {str(e)}")


@app.get("/models")
async def get_available_models():
    """
    Retorna lista de modelos disponíveis

    Returns:
        Lista de modelos
    """
    return {"models": Config.AVAILABLE_MODELS, "default": Config.DEFAULT_MODEL}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
