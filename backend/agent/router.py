"""
Agent Router
Conditional routing logic for LangGraph
"""

from typing import Literal

from backend.agent.state import AgentState
from backend.utils.logger import log


def route_after_classifier(
    state: AgentState
) -> Literal["off_topic", "rag_search"]:
    """
    Routes after classifier node
    
    Decision:
    - If NOT about Koper → off_topic
    - If about Koper → rag_search
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name
    """
    is_about_koper = state.get("is_about_koper", True)
    
    if not is_about_koper:
        log.info("🔀 [ROUTER] Classifier → OFF_TOPIC")
        return "off_topic"
    else:
        log.info("🔀 [ROUTER] Classifier → RAG_SEARCH")
        return "rag_search"


def route_after_evaluator(
    state: AgentState
) -> Literal["generate_answer", "human_handoff"]:
    """
    Routes after evaluator node
    
    Decision:
    - If sufficient info → generate_answer
    - If insufficient info → human_handoff
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name
    """
    has_sufficient_info = state.get("has_sufficient_info", False)
    
    if has_sufficient_info:
        log.info("🔀 [ROUTER] Evaluator → GENERATE_ANSWER")
        return "generate_answer"
    else:
        log.info("🔀 [ROUTER] Evaluator → HUMAN_HANDOFF")
        return "human_handoff"

