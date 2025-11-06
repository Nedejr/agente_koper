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
        Updated state with retrieved documents and images
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
        
        # Extract images from documents with semantic filtering
        images = []
        seen_images = set()  # Avoid duplicates
        
        # Convert user message to lowercase for matching
        query_lower = user_message.lower()
        query_terms = set(query_lower.split())
        
        for doc in documents:
            doc_score = doc.get("score", 0.0)
            doc_images = doc["metadata"].get("images", [])
            
            log.info(f"📄 Document score: {doc_score:.3f} | Images in metadata: {len(doc_images)}")
            
            # Only extract images from reasonably relevant documents (score > 0.4)
            if doc_score < 0.4:
                log.info(f"   ⏭️  Skipping document (score too low: {doc_score:.3f})")
                continue
            
            if not doc_images:
                log.info(f"   ⚠️  Document has no images in metadata")
                continue
            
            for img in doc_images:
                img_key = img.get("filename", "")
                
                if img_key and img_key not in seen_images:
                    # Calculate semantic relevance of image to query
                    relevance_score = _calculate_image_relevance(
                        query_lower,
                        query_terms,
                        img.get("section", ""),
                        img.get("caption", ""),
                        img.get("alt", "")
                    )
                    
                    log.info(f"   🖼️  {img_key[:40]}... relevance: {relevance_score:.3f}")
                    
                    # Only include images with some relevance (> 0.2)
                    if relevance_score > 0.2:
                        images.append({
                            "filename": img.get("filename"),
                            "path": img.get("path"),
                            "section": img.get("section"),
                            "caption": img.get("caption"),
                            "alt": img.get("alt"),
                            "relevance_score": relevance_score,
                        })
                        seen_images.add(img_key)
                        log.info(f"      ✅ Image added! Total now: {len(images)}")
                    else:
                        log.info(f"      ❌ Image rejected (relevance too low: {relevance_score:.3f})")
        
        # Sort images by relevance score (highest first)
        images.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        log.info(f"📊 Total images found after filtering: {len(images)}")
        
        # Limit to top 6 most relevant images
        images = images[:6]
        
        log.info(
            f"✅ [RAG_SEARCH] Retrieved {len(documents)} documents "
            f"with {len(images)} relevant images (avg score: {avg_score:.2f})"
        )
        
        steps = state.get("processing_steps", [])
        steps.append("rag_search")
        
        return {
            "retrieved_documents": documents,
            "context": context,
            "retrieval_score": avg_score,
            "sources": list(set(sources)),  # Unique sources
            "images": images if images else None,
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
            "images": None,
            "processing_steps": steps,
            "error": f"RAG search error: {str(e)}",
        }


def _calculate_image_relevance(
    query: str,
    query_terms: set,
    section: str,
    caption: str,
    alt: str
) -> float:
    """
    Calculate semantic relevance of an image to the user query
    
    Args:
        query: User query in lowercase
        query_terms: Set of query terms
        section: Image section name
        caption: Image caption
        alt: Image alt text
        
    Returns:
        Relevance score between 0 and 1
    """
    score = 0.0
    
    # Combine all image text fields
    image_text = f"{section} {caption} {alt}".lower()
    image_terms = set(image_text.split())
    
    log.info(f"      🔍 Query: '{query[:50]}...' | Section: '{section[:50]}...'")
    
    # 1. Check for exact phrase match in caption/section (high weight)
    if query in image_text:
        score += 0.5
        log.info(f"         ✓ Exact phrase match! +0.5")
    
    # 2. Calculate term overlap (Jaccard similarity)
    # Remove common stopwords
    stopwords = {
        'o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas', 'para', 'com', 'por',
        'e', 'ou', 'que', 'se', 'um', 'uma', 'como', 'é', '?', '!'
    }
    
    query_terms_clean = query_terms - stopwords
    image_terms_clean = image_terms - stopwords
    
    log.info(f"         Query terms: {query_terms_clean}")
    log.info(f"         Image terms: {list(image_terms_clean)[:10]}")
    
    if query_terms_clean and image_terms_clean:
        intersection = query_terms_clean & image_terms_clean
        union = query_terms_clean | image_terms_clean
        jaccard = len(intersection) / len(union) if union else 0
        
        if intersection:
            log.info(f"         ✓ Term overlap: {intersection} | Jaccard: {jaccard:.3f}")
            score += jaccard * 0.4
    
    # 3. Check for key domain terms
    # If query has specific domain terms, give bonus if image has them too
    domain_terms_in_query = query_terms_clean & image_terms_clean
    if len(domain_terms_in_query) >= 2:
        score += 0.2
        log.info(f"         ✓ Domain terms bonus! +0.2")
    
    log.info(f"         → Final score: {score:.3f}")
    
    return min(score, 1.0)  # Cap at 1.0


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

