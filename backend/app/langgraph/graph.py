"""
LangGraph Interview Agent Graph

This module assembles the complete interview workflow graph.
"""

import logging
from typing import Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import InterviewState, create_initial_state
from .nodes import (
    greeting_node,
    info_collection_node,
    profile_validation_node,
    project_analysis_node,
    kpi_extraction_node,
    report_generation_node,
    process_user_input_node
)
from .edges import (
    route_after_greeting,
    route_after_info_collection,
    route_after_profile_validation,
    route_after_project_analysis,
    route_after_kpi_extraction,
    route_after_report_generation,
    route_user_input,
    should_continue
)

logger = logging.getLogger(__name__)


def create_interview_graph(
    checkpointer: Optional[MemorySaver] = None,
    use_sqlite: bool = True
) -> StateGraph:
    """
    Create the complete interview agent graph
    
    Args:
        checkpointer: Optional custom checkpointer
        use_sqlite: Use SQLite for persistence (default: True)
    
    Returns:
        Compiled StateGraph
    """
    
    # Initialize graph with state schema
    workflow = StateGraph(InterviewState)
    
    # Add nodes
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("info_collection", info_collection_node)
    workflow.add_node("profile_validation", profile_validation_node)
    workflow.add_node("project_analysis", project_analysis_node)
    workflow.add_node("kpi_extraction", kpi_extraction_node)
    workflow.add_node("report_generation", report_generation_node)
    workflow.add_node("process_input", process_user_input_node)
    
    # Set entry point
    workflow.set_entry_point("greeting")
    
    # Add conditional edges (routing logic)
    
    # After greeting -> info_collection or wait for input
    workflow.add_conditional_edges(
        "greeting",
        lambda state: "info_collection" if not state.get('waiting_for_input') else END,
        {
            "info_collection": "info_collection",
            END: END
        }
    )
    
    # After info_collection -> stay or move to profile_validation
    workflow.add_conditional_edges(
        "info_collection",
        route_after_info_collection,
        {
            "info_collection": END,  # Wait for more input
            "profile_validation": "profile_validation",
            "end": END
        }
    )
    
    # After profile_validation -> stay or move to project_analysis
    workflow.add_conditional_edges(
        "profile_validation",
        route_after_profile_validation,
        {
            "profile_validation": END,  # Wait for input
            "project_analysis": "project_analysis",
            "end": END
        }
    )
    
    # After project_analysis -> stay or move to kpi_extraction
    workflow.add_conditional_edges(
        "project_analysis",
        route_after_project_analysis,
        {
            "project_analysis": END,  # Wait for input
            "kpi_extraction": "kpi_extraction",
            "end": END
        }
    )
    
    # After kpi_extraction -> stay or move to report_generation
    workflow.add_conditional_edges(
        "kpi_extraction",
        route_after_kpi_extraction,
        {
            "kpi_extraction": END,  # Wait for input
            "report_generation": "report_generation",
            "end": END
        }
    )
    
    # After report_generation -> always end
    workflow.add_edge("report_generation", END)
    
    # Process input routes back to current stage
    workflow.add_conditional_edges(
        "process_input",
        route_user_input,
        {
            "greeting": "greeting",
            "info_collection": "info_collection",
            "profile_validation": "profile_validation",
            "project_analysis": "project_analysis",
            "kpi_extraction": "kpi_extraction",
            "end": END
        }
    )
    
    # Set up checkpointing for state persistence
    if checkpointer is None:
        if use_sqlite:
            # Use SQLite for production persistence
            checkpointer = SqliteSaver.from_conn_string("interview_graph_checkpoints.db")
            logger.info("Using SQLite checkpointer for persistence")
        else:
            # Use in-memory for development
            checkpointer = MemorySaver()
            logger.info("Using in-memory checkpointer")
    
    # Compile the graph
    app = workflow.compile(checkpointer=checkpointer)
    
    logger.info("Interview graph compiled successfully")
    
    return app


# ==================== GRAPH EXECUTION HELPERS ====================

async def start_interview(
    graph,
    cv_text: str,
    jd_text: str,
    session_id: str,
    resume_id: Optional[str] = None
) -> InterviewState:
    """
    Start a new interview session
    
    Args:
        graph: Compiled interview graph
        cv_text: Candidate CV text
        jd_text: Job description text
        session_id: Unique session ID
        resume_id: Optional resume ID
    
    Returns:
        Initial state after greeting
    """
    logger.info(f"[GRAPH] Starting interview session: {session_id}")
    
    # Create initial state
    initial_state = create_initial_state(
        cv_text=cv_text,
        jd_text=jd_text,
        session_id=session_id,
        resume_id=resume_id
    )
    
    # Execute graph (will pause at first waiting_for_input)
    config = {"configurable": {"thread_id": session_id}}
    
    result = await graph.ainvoke(initial_state, config)
    
    logger.info(f"[GRAPH] Interview started, waiting for input")
    return result


async def process_user_response(
    graph,
    session_id: str,
    user_response: str
) -> InterviewState:
    """
    Process user's response and continue interview
    
    Args:
        graph: Compiled interview graph
        session_id: Session ID
        user_response: User's message
    
    Returns:
        Updated state after processing
    """
    logger.info(f"[GRAPH] Processing user response for session: {session_id}")
    
    config = {"configurable": {"thread_id": session_id}}
    
    # Get current state
    current_state = await graph.aget_state(config)
    
    if not current_state:
        raise ValueError(f"Session {session_id} not found")
    
    # Update state with user response
    update = {
        "user_response": user_response,
        "waiting_for_input": False
    }
    
    # Continue execution
    result = await graph.ainvoke(update, config)
    
    logger.info(f"[GRAPH] Response processed, current stage: {result.get('current_stage')}")
    return result


async def get_interview_status(
    graph,
    session_id: str
) -> Optional[InterviewState]:
    """
    Get current state of interview session
    
    Args:
        graph: Compiled interview graph
        session_id: Session ID
    
    Returns:
        Current interview state or None
    """
    config = {"configurable": {"thread_id": session_id}}
    
    try:
        state = await graph.aget_state(config)
        return state.values if state else None
    except Exception as e:
        logger.error(f"Error getting interview status: {str(e)}")
        return None


async def get_interview_history(
    graph,
    session_id: str
) -> list:
    """
    Get full history of interview session (all checkpoints)
    
    Args:
        graph: Compiled interview graph
        session_id: Session ID
    
    Returns:
        List of historical states
    """
    config = {"configurable": {"thread_id": session_id}}
    
    try:
        history = []
        async for state in graph.aget_state_history(config):
            history.append(state.values)
        return history
    except Exception as e:
        logger.error(f"Error getting interview history: {str(e)}")
        return []


# ==================== GRAPH VISUALIZATION ====================

def visualize_graph(graph, output_path: str = "interview_graph.png"):
    """
    Generate visual diagram of the interview graph
    
    Args:
        graph: Compiled interview graph
        output_path: Path to save image
    """
    try:
        from IPython.display import Image, display
        
        # Get graph visualization
        img = Image(graph.get_graph().draw_mermaid_png())
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(img.data)
        
        logger.info(f"Graph visualization saved to {output_path}")
        return img
    except Exception as e:
        logger.error(f"Error visualizing graph: {str(e)}")
        return None


# ==================== GLOBAL GRAPH INSTANCE ====================

_interview_graph = None


def get_interview_graph():
    """
    Get or create global interview graph instance
    
    Returns:
        Compiled interview graph
    """
    global _interview_graph
    
    if _interview_graph is None:
        _interview_graph = create_interview_graph(use_sqlite=True)
        logger.info("Created global interview graph instance")
    
    return _interview_graph
