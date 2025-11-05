"""
Chat API
Endpoints para interação com o chatbot
"""

import time
from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from backend.models.chat import (
    AgentDecision,
    ChatRequest,
    ChatResponse,
    ConversationHistory,
)
from backend.utils.logger import log

router = APIRouter()

# Storage temporário de conversas (em produção, usar Redis ou banco de dados)
conversations: Dict[str, ConversationHistory] = {}


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Enviar mensagem ao chat",
    description="Envia uma mensagem ao agente e recebe resposta"
)
async def chat(request: ChatRequest):
    """
    Endpoint principal de chat
    
    - Recebe mensagem do usuário
    - Processa através do agente LangGraph
    - Retorna resposta com decisão do agente
    """
    start_time = time.time()
    
    # Gera conversation_id se não fornecido
    conversation_id = request.conversation_id or f"conv-{uuid4().hex[:12]}"
    
    log.info(f"💬 Nova mensagem - Conv: {conversation_id} | User: {request.user_id or 'anonymous'}")
    log.debug(f"Mensagem: {request.message}")
    
    try:
        # TODO: Integrar com o agente LangGraph
        # Por enquanto, resposta mock para teste
        
        # Simula processamento
        response_message = (
            "Olá! Sou o assistente do Koper ERP. "
            "Estou em fase de desenvolvimento e em breve poderei ajudá-lo com suas dúvidas sobre o sistema. "
            "Por enquanto, estou apenas testando a infraestrutura básica."
        )
        
        # Calcula tempo de processamento
        processing_time = int((time.time() - start_time) * 1000)
        
        # Cria resposta
        response = ChatResponse(
            conversation_id=conversation_id,
            message=response_message,
            agent_decision=AgentDecision.ANSWER,
            sources=None,
            confidence_score=1.0,
            processing_time_ms=processing_time,
        )
        
        log.info(f"✅ Resposta gerada - Tempo: {processing_time}ms")
        
        return response
        
    except Exception as e:
        log.error(f"❌ Erro ao processar mensagem: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )


@router.get(
    "/chat/history/{conversation_id}",
    response_model=ConversationHistory,
    status_code=status.HTTP_200_OK,
    summary="Obter histórico de conversa",
    description="Retorna o histórico completo de uma conversa"
)
async def get_conversation_history(conversation_id: str):
    """
    Obtém o histórico de uma conversa
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversa {conversation_id} não encontrada"
        )
    
    return conversations[conversation_id]


@router.delete(
    "/chat/history/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Limpar histórico de conversa",
    description="Remove o histórico de uma conversa"
)
async def clear_conversation_history(conversation_id: str):
    """
    Remove o histórico de uma conversa
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        log.info(f"🗑️  Histórico removido - Conv: {conversation_id}")
    
    return None

