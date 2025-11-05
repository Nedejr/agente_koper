"""
Agente Koper - Backend Application
FastAPI + LangChain + LangGraph
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import health, chat, documents
from backend.config import settings
from backend.models.chat import ErrorResponse
from backend.utils.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events: startup e shutdown
    """
    # Startup
    log.info("=" * 60)
    log.info(f"🚀 Iniciando {settings.app_name} v{settings.app_version}")
    log.info(f"🌍 Ambiente: {settings.environment}")
    log.info(f"🔗 Ollama URL: {settings.ollama_base_url}")
    log.info(f"🗄️  Qdrant URL: {settings.qdrant_url}")
    log.info("=" * 60)
    
    # Verificar conexões (opcional)
    # await check_ollama_connection()
    # await check_qdrant_connection()
    
    yield
    
    # Shutdown
    log.info("=" * 60)
    log.info(f"🛑 Encerrando {settings.app_name}")
    log.info("=" * 60)


# ============================================
# FastAPI Application
# ============================================
app = FastAPI(
    title=settings.app_name,
    description="Sistema inteligente de atendimento usando RAG para o Koper ERP",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================
# CORS Middleware
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ============================================
# Request Logging Middleware
# ============================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log de todas as requisições"""
    start_time = datetime.utcnow()
    
    # Log da requisição
    log.info(f"📥 {request.method} {request.url.path}")
    
    # Processa a requisição
    response = await call_next(request)
    
    # Calcula tempo de processamento
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    # Log da resposta
    log.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}ms"
    )
    
    # Adiciona header com tempo de processamento
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    return response


# ============================================
# Global Exception Handler
# ============================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    log.error(f"❌ Erro não tratado: {str(exc)}", exc_info=True)
    
    error_response = ErrorResponse(
        error="Internal Server Error",
        detail=str(exc) if settings.is_development else "Ocorreu um erro interno",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


# ============================================
# Include Routers
# ============================================
# Health check (sem prefixo para facilitar monitoramento)
app.include_router(health.router, tags=["Health"])

# API routes (com prefixo /api)
app.include_router(chat.router, prefix=settings.api_prefix, tags=["Chat"])
app.include_router(documents.router, prefix=settings.api_prefix, tags=["Documents"])


# ============================================
# Root Endpoint
# ============================================
@app.get("/", include_in_schema=False)
async def root():
    """Endpoint raiz - redireciona para docs"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": settings.api_prefix,
    }


# ============================================
# Development Hot Reload
# ============================================
if __name__ == "__main__":
    import uvicorn
    
    log.info("🔥 Modo desenvolvimento - Hot reload ativado")
    
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )

