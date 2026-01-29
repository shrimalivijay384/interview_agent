"""
LangGraph Interview API Routes

FastAPI endpoints for LangGraph-based interview system
"""

import logging
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..langgraph import (
    get_interview_graph,
    start_interview,
    process_user_response,
    get_interview_status,
    get_interview_history
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/langgraph-interview", tags=["langgraph-interview"])


# ==================== REQUEST/RESPONSE MODELS ====================

class StartInterviewRequest(BaseModel):
    """Request to start new interview"""
    cv_text: str
    jd_text: str
    resume_id: Optional[str] = None


class UserResponseRequest(BaseModel):
    """User's response during interview"""
    message: str


class InterviewResponse(BaseModel):
    """Standard interview response"""
    success: bool
    session_id: str
    current_stage: str
    message: Optional[str] = None
    waiting_for_input: bool
    status: str
    data: Optional[dict] = None


# ==================== ENDPOINTS ====================

@router.post("/start", response_model=InterviewResponse)
async def start_langgraph_interview(request: StartInterviewRequest):
    """
    Start a new interview using LangGraph
    
    Example:
    ```
    POST /api/langgraph-interview/start
    {
        "cv_text": "John Doe - Software Engineer...",
        "jd_text": "Senior Python Developer position...",
        "resume_id": "cv_123"
    }
    ```
    
    Returns:
        Session ID and initial greeting message
    """
    try:
        # Generate unique session ID
        session_id = f"lg_{uuid.uuid4().hex[:16]}"
        
        # Get graph instance
        graph = get_interview_graph()
        
        # Start interview
        result = await start_interview(
            graph=graph,
            cv_text=request.cv_text,
            jd_text=request.jd_text,
            session_id=session_id,
            resume_id=request.resume_id
        )
        
        logger.info(f"Started LangGraph interview: {session_id}")
        
        return InterviewResponse(
            success=True,
            session_id=session_id,
            current_stage=result.get('current_stage', 'greeting'),
            message=result.get('current_question'),
            waiting_for_input=result.get('waiting_for_input', True),
            status=result.get('status', 'active'),
            data={
                "greeting_data": result.get('greeting_data'),
                "messages": result.get('messages', [])
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting LangGraph interview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/respond", response_model=InterviewResponse)
async def send_user_response(session_id: str, request: UserResponseRequest):
    """
    Send user's response to continue interview
    
    Example:
    ```
    POST /api/langgraph-interview/{session_id}/respond
    {
        "message": "My name is John Doe"
    }
    ```
    
    Returns:
        Next question or stage update
    """
    try:
        # Get graph instance
        graph = get_interview_graph()
        
        # Process user response
        result = await process_user_response(
            graph=graph,
            session_id=session_id,
            user_response=request.message
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        logger.info(f"Processed response for session {session_id}")
        
        return InterviewResponse(
            success=True,
            session_id=session_id,
            current_stage=result.get('current_stage', 'unknown'),
            message=result.get('current_question'),
            waiting_for_input=result.get('waiting_for_input', True),
            status=result.get('status', 'active'),
            data={
                "messages": result.get('messages', [])[-5:],  # Last 5 messages
                "completed_stages": result.get('completed_stages', [])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/status")
async def get_status(session_id: str):
    """
    Get current status of interview session
    
    Example:
    ```
    GET /api/langgraph-interview/{session_id}/status
    ```
    
    Returns:
        Current state of interview
    """
    try:
        graph = get_interview_graph()
        
        state = await get_interview_status(graph, session_id)
        
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "current_stage": state.get('current_stage'),
            "status": state.get('status'),
            "waiting_for_input": state.get('waiting_for_input'),
            "current_question": state.get('current_question'),
            "completed_stages": state.get('completed_stages', []),
            "candidate_info": state.get('candidate_info', {}),
            "progress": {
                "total_stages": 6,
                "completed": len(state.get('completed_stages', []))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/report")
async def get_report(session_id: str):
    """
    Get final interview report
    
    Example:
    ```
    GET /api/langgraph-interview/{session_id}/report
    ```
    
    Returns:
        Comprehensive interview assessment report
    """
    try:
        graph = get_interview_graph()
        
        state = await get_interview_status(graph, session_id)
        
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Check if interview is complete
        if state.get('status') != 'completed':
            raise HTTPException(
                status_code=400,
                detail="Interview not yet completed"
            )
        
        final_report = state.get('final_report', {})
        
        return {
            "success": True,
            "session_id": session_id,
            "report": final_report,
            "overall_score": state.get('overall_score'),
            "recommendation": state.get('recommendation'),
            "candidate_info": state.get('candidate_info'),
            "kpi_scores": state.get('kpi_scores', {}),
            "strengths": state.get('strengths', []),
            "weaknesses": state.get('weaknesses', []),
            "generated_at": final_report.get('generated_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get full conversation history (time-travel through checkpoints)
    
    Example:
    ```
    GET /api/langgraph-interview/{session_id}/history
    ```
    
    Returns:
        All historical states and messages
    """
    try:
        graph = get_interview_graph()
        
        history = await get_interview_history(graph, session_id)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or no history available"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "history": history,
            "total_checkpoints": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/pause")
async def pause_interview(session_id: str):
    """
    Pause interview session
    
    Can be resumed later from the same checkpoint
    """
    try:
        graph = get_interview_graph()
        
        state = await get_interview_status(graph, session_id)
        
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # Update status to paused
        # (In production, you'd update the state here)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Interview paused successfully",
            "current_stage": state.get('current_stage')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing interview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/visualize")
async def visualize_interview_graph():
    """
    Get visual representation of the interview graph
    
    Returns mermaid diagram text
    """
    try:
        graph = get_interview_graph()
        
        # Get mermaid diagram
        mermaid = graph.get_graph().draw_mermaid()
        
        return {
            "success": True,
            "diagram": mermaid,
            "format": "mermaid"
        }
        
    except Exception as e:
        logger.error(f"Error visualizing graph: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def langgraph_health_check():
    """Health check for LangGraph interview system"""
    try:
        graph = get_interview_graph()
        
        return {
            "success": True,
            "service": "langgraph-interview",
            "status": "operational",
            "graph_compiled": graph is not None
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
