"""
Modelos Pydantic para Chat
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Papel da mensagem no chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Mensagem individual do chat"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request para enviar mensagem ao chat"""
    message: str = Field(..., min_length=1, max_length=5000, description="Mensagem do usuário")
    conversation_id: Optional[str] = Field(default=None, description="ID da conversa (gera automaticamente se não fornecido)")
    user_id: Optional[str] = Field(default=None, description="ID do usuário (opcional)")
    model: Optional[str] = Field(default=None, description="Modelo OpenRouter a usar (opcional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "O que é o Koper ERP?",
                "conversation_id": "conv-123456",
                "user_id": "user-789"
            }
        }


class AgentDecision(str, Enum):
    """Decisão tomada pelo agente"""
    ANSWER = "answer"  # Respondeu com sucesso
    HUMAN_HANDOFF = "human_handoff"  # Precisa de atendimento humano
    OFF_TOPIC = "off_topic"  # Fora do escopo


class ChatResponse(BaseModel):
    """Response do chat"""
    conversation_id: str
    message: str = Field(..., description="Resposta do agente")
    agent_decision: AgentDecision = Field(..., description="Decisão do agente")
    sources: Optional[List[str]] = Field(default=None, description="Fontes utilizadas (documentos)")
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="Confiança na resposta")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[int] = Field(default=None, description="Tempo de processamento em ms")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv-123456",
                "message": "O Koper ERP é um sistema de gestão empresarial...",
                "agent_decision": "answer",
                "sources": ["documento1.pdf", "manual_koper.pdf"],
                "confidence_score": 0.85,
                "timestamp": "2024-01-01T12:00:00",
                "processing_time_ms": 1500
            }
        }


class ConversationHistory(BaseModel):
    """Histórico de uma conversa"""
    conversation_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None


class ConversationSummary(BaseModel):
    """Resumo de uma conversa"""
    conversation_id: str
    message_count: int
    first_message: Optional[str] = None
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HealthCheck(BaseModel):
    """Response do health check"""
    status: str = "healthy"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "environment": "development",
                "timestamp": "2024-01-01T12:00:00",
                "services": {
                    "ollama": "connected",
                    "qdrant": "connected"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response de erro"""
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Internal Server Error",
                "detail": "Erro ao processar mensagem",
                "status_code": 500,
                "timestamp": "2024-01-01T12:00:00"
            }
        }

