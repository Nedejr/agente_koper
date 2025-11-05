"""
Health Check API
Verifica status da aplicação e serviços externos
"""

import httpx
from fastapi import APIRouter, status

from backend.config import settings
from backend.models.chat import HealthCheck
from backend.utils.logger import log

router = APIRouter()


async def check_ollama() -> dict:
    """Verifica conexão com Ollama"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/version")
            if response.status_code == 200:
                return {"status": "connected", "version": response.json().get("version")}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        log.warning(f"Ollama não disponível: {str(e)}")
        return {"status": "disconnected", "error": str(e)}


async def check_qdrant() -> dict:
    """Verifica conexão com Qdrant"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.qdrant_url}/healthz")
            if response.status_code == 200:
                return {"status": "connected"}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        log.warning(f"Qdrant não disponível: {str(e)}")
        return {"status": "disconnected", "error": str(e)}


@router.get(
    "/health",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Verifica o status da aplicação e serviços externos"
)
async def health_check():
    """
    Health check endpoint
    
    Retorna:
    - Status da aplicação
    - Versão
    - Ambiente
    - Status dos serviços externos (Ollama, Qdrant)
    """
    # Verifica serviços externos
    ollama_status = await check_ollama()
    qdrant_status = await check_qdrant()
    
    # Determina status geral
    overall_status = "healthy"
    if ollama_status["status"] != "connected" or qdrant_status["status"] != "connected":
        overall_status = "degraded"
    
    return HealthCheck(
        status=overall_status,
        version=settings.app_version,
        environment=settings.environment,
        services={
            "ollama": ollama_status,
            "qdrant": qdrant_status,
        }
    )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Verifica se a aplicação está viva (para Kubernetes)"
)
async def liveness():
    """
    Liveness probe - verifica se a aplicação está respondendo
    Usado pelo Kubernetes para restart automático
    """
    return {"status": "alive"}


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Verifica se a aplicação está pronta para receber tráfego"
)
async def readiness():
    """
    Readiness probe - verifica se a aplicação está pronta
    Usado pelo Kubernetes para controle de tráfego
    """
    # Verifica se serviços críticos estão disponíveis
    ollama_status = await check_ollama()
    qdrant_status = await check_qdrant()
    
    if ollama_status["status"] == "connected" and qdrant_status["status"] == "connected":
        return {"status": "ready"}
    else:
        return {"status": "not_ready", "services": {
            "ollama": ollama_status["status"],
            "qdrant": qdrant_status["status"],
        }}

