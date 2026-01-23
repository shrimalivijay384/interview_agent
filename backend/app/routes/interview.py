"""
Interview management routes.
"""
import logging
from fastapi import APIRouter, HTTPException
from app.models import (
    StartInterviewRequest, StartInterviewResponse,
    SubmitAnswerRequest, SubmitAnswerResponse,
    EndInterviewRequest, EndInterviewResponse
)
from app.services.jd_parser import parse_jd
from app.services.resume_parser import parse_resume
from app.services.kpi_decider import decide_kpis
from app.services.question_agent import (
    start_interview, get_next_question, finalize_interview,
    get_session_store
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview_endpoint(request: StartInterviewRequest):
    """
    Start a new interview session.
    
    Process:
    1. Parse job description
    2. Parse candidate resume
    3. Decide KPIs based on JD and resume
    4. Initialize interview session
    5. Generate first question
    
    Returns:
        Session ID, first question, and KPI list
    """
    try:
        logger.info("Starting new interview session")
        
        # Step 1: Parse job description
        logger.info("Parsing job description...")
        jd = await parse_jd(request.jd_text)
        
        # Step 2: Parse resume
        logger.info("Parsing resume...")
        resume = await parse_resume(request.cv_text)
        
        # Step 3: Decide KPIs
        logger.info("Determining KPIs...")
        kpis = await decide_kpis(jd, resume)
        
        # Step 4: Start interview
        logger.info("Initializing interview session...")
        session = await start_interview(jd, resume, kpis)
        
        # Get first question
        first_question = session.get_current_question()
        
        if not first_question:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate first question"
            )
        
        logger.info(f"Interview session started: {session.id}")
        
        return StartInterviewResponse(
            session_id=session.id,
            first_question=first_question,
            kpis=kpis,
            message=f"Welcome, {resume.name}! Your interview has started. We'll be evaluating {len(kpis)} key areas."
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start interview: {str(e)}"
        )


@router.post("/answer", response_model=SubmitAnswerResponse)
async def submit_answer_endpoint(request: SubmitAnswerRequest):
    """
    Submit an answer and get the next question.
    
    Process:
    1. Validate session
    2. Evaluate submitted answer
    3. Update KPI scores
    4. Generate next question or complete interview
    
    Returns:
        Next question or completion status with evaluation summary
    """
    try:
        logger.info(f"Submitting answer for session: {request.session_id}")
        
        # Get next question and evaluation
        next_question, is_complete, evaluations = await get_next_question(
            request.session_id,
            request.answer_text,
            request.duration_seconds
        )
        
        # Get session for progress info
        store = get_session_store()
        session = store.get_session(request.session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Build evaluation summary
        eval_summary = None
        if evaluations:
            avg_score = sum(e.score for e in evaluations) / len(evaluations)
            eval_summary = f"Answer evaluated. Average score: {avg_score:.2f}/5.0"
        
        # Build progress info
        total_questions = len(session.question_history)
        kpi_coverage = {}
        for kpi in session.kpis:
            scores = session.kpi_scores.get(kpi.id, [])
            kpi_coverage[kpi.name] = {
                "evaluations": len(scores),
                "avg_score": sum(scores) / len(scores) if scores else 0
            }
        
        progress = {
            "total_questions": total_questions,
            "kpi_coverage": kpi_coverage
        }
        
        response = SubmitAnswerResponse(
            session_id=request.session_id,
            next_question=next_question,
            evaluation_summary=eval_summary,
            is_complete=is_complete,
            progress=progress
        )
        
        if is_complete:
            logger.info(f"Interview completed: {request.session_id}")
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.post("/end", response_model=EndInterviewResponse)
async def end_interview_endpoint(request: EndInterviewRequest):
    """
    End interview and generate final report.
    
    Process:
    1. Validate session
    2. Calculate final scores
    3. Generate comprehensive feedback
    4. Provide hiring recommendation
    
    Returns:
        Final report with scores, strengths, weaknesses, and recommendation
    """
    try:
        logger.info(f"Ending interview session: {request.session_id}")
        
        # Generate final report
        report = await finalize_interview(request.session_id)
        
        logger.info(f"Interview ended. Final score: {report.overall_score:.2f}/5.0")
        
        return EndInterviewResponse(
            session_id=request.session_id,
            report=report
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ending interview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end interview: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get information about an interview session.
    
    Returns:
        Session status and basic information
    """
    try:
        store = get_session_store()
        session = store.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.id,
            "status": session.status,
            "candidate_name": session.resume.name,
            "job_title": session.jd.title,
            "total_questions": len(session.question_history),
            "kpis_count": len(session.kpis),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )
