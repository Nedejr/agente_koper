"""
Chat API
Endpoints for chatbot interaction with LangGraph agent
"""

import time
from datetime import datetime
from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from backend.agent.graph import run_agent
from backend.models.chat import (
    AgentDecision,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    MessageRole,
)
from backend.utils.logger import log

router = APIRouter()

# Temporary conversation storage (use Redis or database in production)
conversations: Dict[str, ConversationHistory] = {}


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to chat",
    description="Send a message to the agent and receive response"
)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    - Receives user message
    - Processes through LangGraph agent
    - Returns response with agent decision
    """
    start_time = time.time()
    
    # Generate conversation_id if not provided
    conversation_id = request.conversation_id or f"conv-{uuid4().hex[:12]}"
    
    log.info(f"💬 New message - Conv: {conversation_id} | User: {request.user_id or 'anonymous'}")
    log.debug(f"Message: {request.message}")
    
    try:
        # Run LangGraph agent
        agent_result = await run_agent(
            user_message=request.message,
            conversation_id=conversation_id
        )
        
        # Extract response from agent state
        response_message = agent_result.get("response", "Sorry, I couldn't generate a response.")
        agent_decision_str = agent_result.get("agent_decision", "answer")
        sources = agent_result.get("sources", [])
        evaluator_confidence = agent_result.get("evaluator_confidence")
        
        # Map agent decision to enum
        decision_map = {
            "answer": AgentDecision.ANSWER,
            "human_handoff": AgentDecision.HUMAN_HANDOFF,
            "off_topic": AgentDecision.OFF_TOPIC,
        }
        agent_decision = decision_map.get(agent_decision_str, AgentDecision.ANSWER)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Store conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = ConversationHistory(
                conversation_id=conversation_id,
                messages=[],
                user_id=request.user_id,
            )
        
        # Add messages to history
        conversations[conversation_id]["messages"].append(
            ChatMessage(role=MessageRole.USER, content=request.message)
        )
        conversations[conversation_id]["messages"].append(
            ChatMessage(role=MessageRole.ASSISTANT, content=response_message)
        )
        conversations[conversation_id]["updated_at"] = datetime.utcnow()
        
        # Create response
        response = ChatResponse(
            conversation_id=conversation_id,
            message=response_message,
            agent_decision=agent_decision,
            sources=sources if sources else None,
            confidence_score=evaluator_confidence,
            processing_time_ms=processing_time,
        )
        
        log.info(
            f"✅ Response generated - "
            f"Decision: {agent_decision.value} | "
            f"Time: {processing_time}ms"
        )
        
        return response
        
    except Exception as e:
        log.error(f"❌ Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
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

