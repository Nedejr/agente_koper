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
    
    # Model metadata
    models_info = [
        {
            "id": "meta-llama/llama-3.1-8b-instruct:free",
            "name": "Meta Llama 3.1 8B",
            "description": "Excelente para conversação e atendimento",
            "context": "128k tokens",
            "recommended": True,
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
            "id": "qwen/qwen-2.5-7b-instruct:free",
            "name": "Qwen 2.5 7B",
            "description": "Bom balanço qualidade/velocidade",
            "context": "32k tokens",
            "recommended": False,
        },
        {
            "id": "microsoft/phi-3-medium-128k-instruct:free",
            "name": "Microsoft Phi-3 Medium",
            "description": "Grande contexto, ótimo para documentos",
            "context": "128k tokens",
            "recommended": False,
        },
        {
            "id": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo:free",
            "name": "Nous Hermes 2 Mixtral",
            "description": "Poderoso, mas mais lento",
            "context": "32k tokens",
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

