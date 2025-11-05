"""
Agent State
Defines the state structure for LangGraph agent
"""

from typing import List, Optional, TypedDict


class AgentState(TypedDict):
    """
    State maintained throughout the agent execution
    
    This state is passed between nodes in the LangGraph
    """
    
    # Input
    user_message: str
    conversation_id: str
    
    # Classification
    is_about_koper: Optional[bool]
    classifier_confidence: Optional[float]
    
    # RAG
    retrieved_documents: Optional[List[dict]]
    context: Optional[str]
    retrieval_score: Optional[float]
    
    # Evaluation
    has_sufficient_info: Optional[bool]
    evaluator_confidence: Optional[float]
    
    # Response
    response: Optional[str]
    agent_decision: Optional[str]  # "answer", "human_handoff", "off_topic"
    
    # Metadata
    sources: Optional[List[str]]
    processing_steps: Optional[List[str]]
    error: Optional[str]


class ConversationMessage(TypedDict):
    """
    Single message in conversation history
    """
    role: str  # "user" or "assistant"
    content: str


# Initial state factory
def create_initial_state(
    user_message: str,
    conversation_id: str
) -> AgentState:
    """
    Create initial agent state
    
    Args:
        user_message: User's input message
        conversation_id: Unique conversation identifier
        
    Returns:
        Initial AgentState
    """
    return AgentState(
        user_message=user_message,
        conversation_id=conversation_id,
        is_about_koper=None,
        classifier_confidence=None,
        retrieved_documents=None,
        context=None,
        retrieval_score=None,
        has_sufficient_info=None,
        evaluator_confidence=None,
        response=None,
        agent_decision=None,
        sources=None,
        processing_steps=[],
        error=None,
    )

