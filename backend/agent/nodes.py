"""
Agent Nodes
Implementation of all LangGraph agent nodes
"""

from typing import Any, Dict

from backend.agent.state import AgentState
from backend.config import settings
from backend.llm.openrouter_client import openrouter_client
from backend.llm.prompts import (
    CLASSIFIER_PROMPT,
    OFF_TOPIC_RESPONSE,
    HUMAN_HANDOFF_RESPONSE,
    build_rag_prompt,
    build_evaluator_prompt,
)
from backend.rag.retriever import retriever
from backend.utils.logger import log


async def classifier_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Classifier
    Classifies if the user message is about Koper ERP
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with classification
    """
    log.info("🔍 [CLASSIFIER] Analyzing user intent")
    
    try:
        user_message = state["user_message"]
        
        # Build classifier prompt
        prompt = CLASSIFIER_PROMPT.format(message=user_message)
        
        # Get selected model or use default
        model = state.get("selected_model") or settings.openrouter_default_model
        
        # Call LLM via OpenRouter
        response = await openrouter_client.generate(
            prompt=prompt,
            temperature=0.1,  # Low temperature for consistent classification
            model=model,
        )
        
        # Parse response (should be "SIM" or "NAO")
        response_clean = response.strip().upper()
        is_about_koper = "SIM" in response_clean or "YES" in response_clean
        
        # Calculate simple confidence based on response
        confidence = 0.9 if is_about_koper else 0.8
        
        log.info(
            f"✅ [CLASSIFIER] Result: {'About Koper' if is_about_koper else 'Off-topic'} "
            f"(confidence: {confidence:.2f})"
        )
        
        # Update processing steps
        steps = state.get("processing_steps", [])
        steps.append("classifier")
        
        return {
            "is_about_koper": is_about_koper,
            "classifier_confidence": confidence,
            "processing_steps": steps,
        }
        
    except Exception as e:
        log.error(f"❌ [CLASSIFIER] Error: {str(e)}")
        steps = state.get("processing_steps", [])
        steps.append("classifier_error")
        return {
            "is_about_koper": True,  # Default to True on error to proceed
            "classifier_confidence": 0.5,
            "processing_steps": steps,
            "error": f"Classifier error: {str(e)}",
        }


async def off_topic_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Off-Topic Response
    Handles messages not related to Koper ERP
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with off-topic response
    """
    log.info("🚫 [OFF_TOPIC] Generating off-topic response")
    
    steps = state.get("processing_steps", [])
    steps.append("off_topic_response")
    
    return {
        "response": OFF_TOPIC_RESPONSE,
        "agent_decision": "off_topic",
        "processing_steps": steps,
    }


async def rag_search_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: RAG Search
    Retrieves relevant documents from vector store
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with retrieved documents
    """
    log.info("📚 [RAG_SEARCH] Searching for relevant documents")
    
    try:
        user_message = state["user_message"]
        
        # Retrieve documents
        retrieval_result = await retriever.retrieve_with_context(
            query=user_message,
            top_k=settings.top_k_results,
            score_threshold=settings.min_similarity_score,
        )
        
        documents = retrieval_result["documents"]
        context = retrieval_result["context"]
        avg_score = retrieval_result["avg_score"]
        
        # Extract sources
        sources = [
            doc["metadata"].get("filename", "Unknown")
            for doc in documents
        ]
        
        log.info(
            f"✅ [RAG_SEARCH] Retrieved {len(documents)} documents "
            f"(avg score: {avg_score:.2f})"
        )
        
        steps = state.get("processing_steps", [])
        steps.append("rag_search")
        
        return {
            "retrieved_documents": documents,
            "context": context,
            "retrieval_score": avg_score,
            "sources": list(set(sources)),  # Unique sources
            "processing_steps": steps,
        }
        
    except Exception as e:
        log.error(f"❌ [RAG_SEARCH] Error: {str(e)}")
        steps = state.get("processing_steps", [])
        steps.append("rag_search_error")
        return {
            "retrieved_documents": [],
            "context": "No documents found due to error.",
            "retrieval_score": 0.0,
            "sources": [],
            "processing_steps": steps,
            "error": f"RAG search error: {str(e)}",
        }


async def evaluator_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 4: Evaluator
    Evaluates if retrieved documents have sufficient information
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with evaluation
    """
    log.info("⚖️  [EVALUATOR] Evaluating document quality")
    
    try:
        user_message = state["user_message"]
        documents = state.get("retrieved_documents", [])
        
        # Check if we have documents
        if not documents:
            log.warning("[EVALUATOR] No documents to evaluate")
            steps = state.get("processing_steps", [])
            steps.append("evaluator_no_docs")
            return {
                "has_sufficient_info": False,
                "evaluator_confidence": 0.0,
                "processing_steps": steps,
            }
        
        # Build evaluator prompt
        prompt = build_evaluator_prompt(user_message, documents)
        
        # Get selected model or use default
        model = state.get("selected_model") or settings.openrouter_default_model
        
        # Call LLM via OpenRouter
        response = await openrouter_client.generate(
            prompt=prompt,
            temperature=0.1,
            model=model,
        )
        
        # Parse confidence score
        try:
            confidence_score = float(response.strip())
            confidence_score = max(0.0, min(1.0, confidence_score))  # Clamp to [0, 1]
        except ValueError:
            log.warning(f"[EVALUATOR] Could not parse score: {response}")
            confidence_score = 0.5
        
        # Determine if info is sufficient
        has_sufficient_info = confidence_score >= settings.evaluator_min_confidence
        
        log.info(
            f"✅ [EVALUATOR] Confidence: {confidence_score:.2f} "
            f"({'Sufficient' if has_sufficient_info else 'Insufficient'})"
        )
        
        steps = state.get("processing_steps", [])
        steps.append("evaluator")
        
        return {
            "has_sufficient_info": has_sufficient_info,
            "evaluator_confidence": confidence_score,
            "processing_steps": steps,
        }
        
    except Exception as e:
        log.error(f"❌ [EVALUATOR] Error: {str(e)}")
        # Em caso de erro (rate limit, etc), assume que documentos são suficientes
        # se foram recuperados com score razoável
        steps = state.get("processing_steps", [])
        steps.append("evaluator_error")
        
        # Se temos documentos com score > 0.5, considera suficiente mesmo com erro no evaluator
        retrieval_score = state.get("retrieval_score", 0.0)
        has_sufficient = retrieval_score >= 0.5
        
        return {
            "has_sufficient_info": has_sufficient,
            "evaluator_confidence": retrieval_score if has_sufficient else 0.0,
            "processing_steps": steps,
            "error": f"Evaluator error (using fallback): {str(e)}",
        }


async def generate_answer_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 5: Generate Answer
    Generates answer based on retrieved documents
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with generated answer
    """
    log.info("💬 [GENERATE_ANSWER] Generating response from RAG")
    
    try:
        user_message = state["user_message"]
        context = state.get("context", "")
        
        # Build RAG prompt
        prompt = build_rag_prompt(user_message, state.get("retrieved_documents", []))
        
        # Get selected model or use default
        model = state.get("selected_model") or settings.openrouter_default_model
        
        # Generate response
        response = await openrouter_client.generate(
            prompt=prompt,
            temperature=settings.openrouter_temperature,
            model=model,
        )
        
        log.info("✅ [GENERATE_ANSWER] Response generated successfully")
        
        steps = state.get("processing_steps", [])
        steps.append("generate_answer")
        
        return {
            "response": response.strip(),
            "agent_decision": "answer",
            "processing_steps": steps,
        }
        
    except Exception as e:
        log.error(f"❌ [GENERATE_ANSWER] Error: {str(e)}")
        steps = state.get("processing_steps", [])
        steps.append("generate_answer_error")
        return {
            "response": "Desculpe, ocorreu um erro ao gerar a resposta. Por favor, tente novamente.",
            "agent_decision": "answer",
            "processing_steps": steps,
            "error": f"Generate answer error: {str(e)}",
        }


async def human_handoff_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 6: Human Handoff
    Directs user to human support when information is insufficient
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with handoff message
    """
    log.info("🤝 [HUMAN_HANDOFF] Directing to human support")
    
    steps = state.get("processing_steps", [])
    steps.append("human_handoff")
    
    return {
        "response": HUMAN_HANDOFF_RESPONSE,
        "agent_decision": "human_handoff",
        "processing_steps": steps,
    }

