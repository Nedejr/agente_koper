"""
Models API
Endpoints for model management
"""

from fastapi import APIRouter, status

from backend.config import settings
from backend.utils.logger import log

router = APIRouter()


@router.get(
    "/models",
    status_code=status.HTTP_200_OK,
    summary="List available models",
    description="List all available free models from OpenRouter"
)
async def list_models():
    """
    List available free models
    
    Returns list of models that can be selected
    """
    models = settings.openrouter_free_models
    
    # Model metadata (verified working on OpenRouter)
    models_info = [
        {
            "id": "meta-llama/llama-3.2-3b-instruct:free",
            "name": "Meta Llama 3.2 3B",
            "description": "Rápido e eficiente para conversação",
            "context": "128k tokens",
            "recommended": True,
        },
        {
            "id": "meta-llama/llama-3.2-1b-instruct:free",
            "name": "Meta Llama 3.2 1B",
            "description": "Muito rápido, ideal para respostas simples",
            "context": "128k tokens",
            "recommended": False,
        },
        {
            "id": "google/gemma-2-9b-it:free",
            "name": "Google Gemma 2 9B",
            "description": "Ótimo raciocínio e instruções complexas",
            "context": "8k tokens",
            "recommended": True,
        },
        {
            "id": "mistralai/mistral-7b-instruct:free",
            "name": "Mistral 7B",
            "description": "Compacto e eficiente para RAG",
            "context": "32k tokens",
            "recommended": False,
        },
        {
            "id": "qwen/qwen-2-7b-instruct:free",
            "name": "Qwen 2 7B",
            "description": "Bom balanço qualidade/velocidade",
            "context": "32k tokens",
            "recommended": False,
        },
        {
            "id": "microsoft/phi-3-mini-128k-instruct:free",
            "name": "Microsoft Phi-3 Mini",
            "description": "Grande contexto, compacto",
            "context": "128k tokens",
            "recommended": False,
        },
    ]
    
    return {
        "models": models_info,
        "default": settings.openrouter_default_model,
        "total": len(models_info),
    }


@router.get(
    "/models/current",
    status_code=status.HTTP_200_OK,
    summary="Get current model",
    description="Get the currently selected default model"
)
async def get_current_model():
    """
    Get current default model
    """
    return {
        "model": settings.openrouter_default_model,
    }

