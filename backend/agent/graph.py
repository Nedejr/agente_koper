"""
Agent Graph
LangGraph workflow definition
"""

from langgraph.graph import END, StateGraph

from backend.agent.nodes import (
    classifier_node,
    off_topic_node,
    rag_search_node,
    evaluator_node,
    generate_answer_node,
    human_handoff_node,
)
from backend.agent.router import route_after_classifier, route_after_evaluator
from backend.agent.state import AgentState
from backend.utils.logger import log


def create_agent_graph() -> StateGraph:
    """
    Creates the LangGraph agent workflow
    
    Graph Structure:
    
    START
      ↓
    CLASSIFIER
      ├─ Not about Koper → OFF_TOPIC → END
      └─ About Koper → RAG_SEARCH
                         ↓
                       EVALUATOR
                         ├─ Sufficient → GENERATE_ANSWER → END
                         └─ Insufficient → HUMAN_HANDOFF → END
    
    Returns:
        Compiled StateGraph
    """
    log.info("🔧 Creating LangGraph agent workflow")
    
    # Initialize graph with state
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("off_topic", off_topic_node)
    workflow.add_node("rag_search", rag_search_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("human_handoff", human_handoff_node)
    
    # Set entry point
    workflow.set_entry_point("classifier")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "classifier",
        route_after_classifier,
        {
            "off_topic": "off_topic",
            "rag_search": "rag_search",
        }
    )
    
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluator,
        {
            "generate_answer": "generate_answer",
            "human_handoff": "human_handoff",
        }
    )
    
    # Add normal edges
    workflow.add_edge("off_topic", END)
    workflow.add_edge("rag_search", "evaluator")
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("human_handoff", END)
    
    # Compile graph
    app = workflow.compile()
    
    log.info("✅ LangGraph agent workflow created successfully")
    
    return app


# Create global agent instance
agent_graph = create_agent_graph()


async def run_agent(user_message: str, conversation_id: str) -> AgentState:
    """
    Run the agent workflow
    
    Args:
        user_message: User's input message
        conversation_id: Conversation identifier
        
    Returns:
        Final agent state with response
    """
    from backend.agent.state import create_initial_state
    
    log.info(f"🚀 Starting agent execution - Conv: {conversation_id}")
    
    # Create initial state
    initial_state = create_initial_state(user_message, conversation_id)
    
    # Run graph
    final_state = await agent_graph.ainvoke(initial_state)
    
    # Log execution summary
    steps = final_state.get("processing_steps", [])
    decision = final_state.get("agent_decision", "unknown")
    
    log.info(
        f"✅ Agent execution completed - "
        f"Decision: {decision} | "
        f"Steps: {' → '.join(steps)}"
    )
    
    return final_state

