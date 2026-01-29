"""
Unified Interview Orchestrator - Coordinates all interview agents
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.models import (
    UnifiedInterviewSession, OrchestratorStage, OrchestratorRequest,
    OrchestratorResponse
)
from app.services.info_collector_agent import get_info_collector_agent
from app.services.profile_validator import get_profile_validator_agent
from app.services.project_analyzer_agent import get_project_analyzer_agent
from app.services.kpi_extractor_agent import get_kpi_extractor_agent
from app.services.interview_agent import get_interview_agent

logger = logging.getLogger(__name__)


class InterviewOrchestrator:
    """
    Unified Interview Orchestrator
    
    Coordinates the complete interview flow:
    1. Greeting & Info Collection
    2. Profile Validation (LinkedIn + GitHub)
    3. Project Analysis (Technical Deep Dive)
    4. KPI Extraction (from Job Description)
    5. Technical Interview (KPI-based Q&A)
    6. Final Report Generation
    """
    
    def __init__(self):
        self.sessions: Dict[str, UnifiedInterviewSession] = {}
        
        # Initialize all agents
        self.greeting_agent = get_info_collector_agent()
        self.validator_agent = get_profile_validator_agent()
        self.project_agent = get_project_analyzer_agent()
        self.kpi_agent = get_kpi_extractor_agent()
        self.interview_agent = get_interview_agent()
        
        logger.info("Interview Orchestrator initialized with all agents")
    
    
    async def start_interview(
        self,
        session_id: str,
        jd_text: Optional[str] = None,
        resume_id: Optional[int] = None
    ) -> OrchestratorResponse:
        """
        Start a new unified interview session
        
        Args:
            session_id: Unique session identifier
            jd_text: Optional job description text
            resume_id: Optional resume ID from database
            
        Returns:
            OrchestratorResponse with greeting message
        """
        try:
            logger.info(f"[{session_id}] Starting unified interview")
            
            # Create unified session
            session = UnifiedInterviewSession(
                session_id=session_id,
                current_stage=OrchestratorStage.GREETING,
                jd_text=jd_text,
                resume_id=resume_id
            )
            
            self.sessions[session_id] = session
            
            # Start greeting stage
            greeting_session_id = f"{session_id}_greeting"
            greeting_response = self.greeting_agent.start_greeting(
                session_id=greeting_session_id
            )
            
            session.greeting_session_id = greeting_session_id
            session.stage_history.append({
                "stage": "greeting",
                "timestamp": datetime.utcnow().isoformat(),
                "action": "started"
            })
            
            logger.info(f"[{session_id}] Interview started with greeting stage")
            
            return OrchestratorResponse(
                session_id=session_id,
                current_stage="greeting",
                message="Welcome! Let's begin the interview process.",
                agent_response=greeting_response.model_dump() if hasattr(greeting_response, 'model_dump') else greeting_response,
                next_action="provide_greeting_response",
                progress={
                    "total_stages": 6,
                    "completed_stages": 0,
                    "current_stage": 1,
                    "stage_name": "Greeting & Info Collection"
                },
                completed=False
            )
            
        except Exception as e:
            logger.error(f"[{session_id}] Error starting interview: {str(e)}")
            raise ValueError(f"Failed to start interview: {str(e)}")
    
    
    async def process_action(
        self,
        session_id: str,
        action: str,
        data: Optional[Dict[str, Any]] = None
    ) -> OrchestratorResponse:
        """
        Process an action in the interview flow
        
        Args:
            session_id: Session identifier
            action: Action to perform
            data: Action data
            
        Returns:
            OrchestratorResponse with next step
        """
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            session = self.sessions[session_id]
            
            logger.info(f"[{session_id}] Processing action: {action} at stage: {session.current_stage}")
            
            # Route to appropriate stage handler
            if session.current_stage == OrchestratorStage.GREETING:
                return await self._handle_greeting_stage(session, action, data)
            
            elif session.current_stage == OrchestratorStage.INFO_COLLECTION:
                return await self._handle_info_collection_stage(session, action, data)
            
            elif session.current_stage == OrchestratorStage.PROFILE_VALIDATION:
                return await self._handle_profile_validation_stage(session, action, data)
            
            elif session.current_stage == OrchestratorStage.PROJECT_ANALYSIS:
                return await self._handle_project_analysis_stage(session, action, data)
            
            elif session.current_stage == OrchestratorStage.KPI_EXTRACTION:
                return await self._handle_kpi_extraction_stage(session, action, data)
            
            elif session.current_stage == OrchestratorStage.TECHNICAL_INTERVIEW:
                return await self._handle_technical_interview_stage(session, action, data)
            
            elif session.current_stage == OrchestratorStage.FINAL_REPORT:
                return await self._handle_final_report_stage(session, action, data)
            
            else:
                raise ValueError(f"Unknown stage: {session.current_stage}")
            
        except Exception as e:
            logger.error(f"[{session_id}] Error processing action: {str(e)}")
            raise ValueError(f"Failed to process action: {str(e)}")
    
    
    async def _handle_greeting_stage(
        self,
        session: UnifiedInterviewSession,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> OrchestratorResponse:
        """Handle greeting and basic info collection stage."""
        try:
            if action == "submit_greeting_response":
                # Collect basic info
                basic_info_response = self.greeting_agent.collect_basic_info(
                    session_id=session.greeting_session_id,
                    user_message=data.get("response", "")
                )
                
                # Store candidate name
                if basic_info_response.get("basic_info"):
                    session.candidate_name = basic_info_response["basic_info"].get("name")
                
                # Move to info collection
                session.current_stage = OrchestratorStage.INFO_COLLECTION
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="info_collection",
                    message="Thank you! Now let's gather some information.",
                    agent_response=basic_info_response if isinstance(basic_info_response, dict) else (basic_info_response.model_dump() if hasattr(basic_info_response, 'model_dump') else {}),
                    next_action="provide_info",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            raise ValueError(f"Invalid action for greeting stage: {action}")
            
        except Exception as e:
            logger.error(f"Error in greeting stage: {str(e)}")
            raise
    
    
    async def _handle_info_collection_stage(
        self,
        session: UnifiedInterviewSession,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> OrchestratorResponse:
        """Handle information collection stage."""
        try:
            if action == "submit_basic_info":
                # Store basic info and cross-check with resume
                basic_info = data.get("basic_info", {})
                session.basic_info = basic_info
                
                # Cross-check with resume
                cross_check_response = self.greeting_agent.cross_check_with_resume(
                    session_id=session.greeting_session_id,
                    basic_info=basic_info,
                    resume_id=session.resume_id
                )
                
                # Move to profile validation
                session.current_stage = OrchestratorStage.PROFILE_VALIDATION
                
                validator_session_id = f"{session.session_id}_validator"
                session.validator_session_id = validator_session_id
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="profile_validation",
                    message="Great! Now let's validate your professional profiles.",
                    agent_response=cross_check_response if isinstance(cross_check_response, dict) else (cross_check_response.model_dump() if hasattr(cross_check_response, 'model_dump') else {}),
                    next_action="provide_linkedin_url",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            raise ValueError(f"Invalid action for info_collection stage: {action}")
            
        except Exception as e:
            logger.error(f"Error in info_collection stage: {str(e)}")
            raise
    
    
    async def _handle_profile_validation_stage(
        self,
        session: UnifiedInterviewSession,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> OrchestratorResponse:
        """Handle profile validation stage."""
        try:
            if action == "submit_linkedin_url":
                # Validate LinkedIn
                linkedin_response = self.validator_agent.validate_linkedin(
                    session_id=session.validator_session_id,
                    linkedin_url=data.get("linkedin_url", ""),
                    candidate_name=session.candidate_name
                )
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="profile_validation",
                    message="LinkedIn validated! Now provide your GitHub profile.",
                    agent_response=linkedin_response.model_dump() if hasattr(linkedin_response, 'model_dump') else linkedin_response,
                    next_action="provide_github_url",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            elif action == "submit_github_url":
                # Validate GitHub
                github_response = self.validator_agent.validate_github(
                    session_id=session.validator_session_id,
                    github_username=data.get("github_username", ""),
                    candidate_name=session.candidate_name
                )
                
                # Get complete validation report
                validation_report = self.validator_agent.generate_complete_report(
                    session_id=session.validator_session_id
                )
                
                session.profile_validation = validation_report.model_dump()
                
                # Move to project analysis
                session.current_stage = OrchestratorStage.PROJECT_ANALYSIS
                
                project_session_id = f"{session.session_id}_project"
                session.project_session_id = project_session_id
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="project_analysis",
                    message="Profiles validated! Let's analyze your projects.",
                    agent_response={"validation_complete": True, "report": validation_report.model_dump()},
                    next_action="start_project_analysis",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            raise ValueError(f"Invalid action for profile_validation stage: {action}")
            
        except Exception as e:
            logger.error(f"Error in profile_validation stage: {str(e)}")
            raise
    
    
    async def _handle_project_analysis_stage(
        self,
        session: UnifiedInterviewSession,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> OrchestratorResponse:
        """Handle project analysis stage."""
        try:
            if action == "start_project_analysis":
                # Start project analysis
                project_response = self.project_agent.start_analysis(
                    session_id=session.project_session_id,
                    candidate_name=session.candidate_name,
                    resume_id=session.resume_id
                )
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="project_analysis",
                    message="Project analysis started. Answer the questions about your projects.",
                    agent_response=project_response.model_dump() if hasattr(project_response, 'model_dump') else project_response,
                    next_action="answer_project_question",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            elif action == "submit_project_answer":
                # Submit answer to project question
                answer_response = self.project_agent.submit_answer(
                    session_id=session.project_session_id,
                    question_id=data.get("question_id", ""),
                    answer=data.get("answer", "")
                )
                
                # Check if project analysis is complete
                if answer_response.get("stage") == "complete":
                    # Get project analysis report
                    project_report = self.project_agent.generate_report(
                        session_id=session.project_session_id
                    )
                    
                    session.project_analysis = project_report.model_dump()
                    
                    # Move to KPI extraction
                    session.current_stage = OrchestratorStage.KPI_EXTRACTION
                    
                    kpi_session_id = f"{session.session_id}_kpi"
                    session.kpi_session_id = kpi_session_id
                    
                    return OrchestratorResponse(
                        session_id=session.session_id,
                        current_stage="kpi_extraction",
                        message="Project analysis complete! Extracting interview KPIs from job description.",
                        agent_response={"project_complete": True, "report": project_report.model_dump()},
                        next_action="extract_kpis",
                        progress=self._get_progress(session),
                        completed=False
                    )
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="project_analysis",
                    message="Answer recorded. Next question.",
                    agent_response=answer_response.model_dump() if hasattr(answer_response, 'model_dump') else answer_response,
                    next_action="answer_project_question",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            raise ValueError(f"Invalid action for project_analysis stage: {action}")
            
        except Exception as e:
            logger.error(f"Error in project_analysis stage: {str(e)}")
            raise
    
    
    async def _handle_kpi_extraction_stage(
        self,
        session: UnifiedInterviewSession,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> OrchestratorResponse:
        """Handle KPI extraction stage."""
        try:
            if action == "extract_kpis":
                if not session.jd_text:
                    raise ValueError("Job description text required for KPI extraction")
                
                # Run full KPI extraction
                kpi_response = self.kpi_agent.run_full_extraction(
                    jd_text=session.jd_text,
                    session_id=session.kpi_session_id,
                    resume_context=session.basic_info
                )
                
                session.kpi_extraction = kpi_response.model_dump()
                
                # Move to technical interview
                session.current_stage = OrchestratorStage.TECHNICAL_INTERVIEW
                
                interview_session_id = f"{session.session_id}_interview"
                session.interview_session_id = interview_session_id
                
                # Start technical interview
                interview_start = self.interview_agent.start_interview(
                    session_id=interview_session_id,
                    candidate_name=session.candidate_name,
                    job_title=kpi_response.job_description.title,
                    kpis=kpi_response.kpis,
                    num_questions=10,
                    context={
                        "basic_info": session.basic_info,
                        "profile_validation": session.profile_validation,
                        "project_analysis": session.project_analysis
                    }
                )
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="technical_interview",
                    message=f"KPIs extracted! Starting technical interview with {len(kpi_response.kpis)} focus areas.",
                    agent_response=interview_start.model_dump(),
                    next_action="answer_interview_question",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            raise ValueError(f"Invalid action for kpi_extraction stage: {action}")
            
        except Exception as e:
            logger.error(f"Error in kpi_extraction stage: {str(e)}")
            raise
    
    
    async def _handle_technical_interview_stage(
        self,
        session: UnifiedInterviewSession,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> OrchestratorResponse:
        """Handle technical interview stage."""
        try:
            if action == "submit_interview_answer":
                # Submit answer to interview question
                answer_response = self.interview_agent.submit_answer(
                    session_id=session.interview_session_id,
                    question_id=data.get("question_id", ""),
                    answer_text=data.get("answer", "")
                )
                
                # Check if interview is complete
                if answer_response.stage == "completed":
                    # Generate interview report
                    interview_report = self.interview_agent.generate_report(
                        session_id=session.interview_session_id
                    )
                    
                    session.interview_results = interview_report.model_dump()
                    
                    # Move to final report
                    session.current_stage = OrchestratorStage.FINAL_REPORT
                    
                    return OrchestratorResponse(
                        session_id=session.session_id,
                        current_stage="final_report",
                        message="Technical interview complete! Generating comprehensive final report.",
                        agent_response={"interview_complete": True, "report": interview_report.model_dump()},
                        next_action="generate_final_report",
                        progress=self._get_progress(session),
                        completed=False
                    )
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="technical_interview",
                    message="Answer recorded. Next question.",
                    agent_response=answer_response.model_dump(),
                    next_action="answer_interview_question",
                    progress=self._get_progress(session),
                    completed=False
                )
            
            raise ValueError(f"Invalid action for technical_interview stage: {action}")
            
        except Exception as e:
            logger.error(f"Error in technical_interview stage: {str(e)}")
            raise
    
    
    async def _handle_final_report_stage(
        self,
        session: UnifiedInterviewSession,
        action: str,
        data: Optional[Dict[str, Any]]
    ) -> OrchestratorResponse:
        """Handle final report generation stage."""
        try:
            if action == "generate_final_report":
                # Compile all data into final comprehensive report
                final_report = {
                    "session_id": session.session_id,
                    "candidate_name": session.candidate_name,
                    "basic_info": session.basic_info,
                    "profile_validation": session.profile_validation,
                    "project_analysis": session.project_analysis,
                    "kpi_extraction": session.kpi_extraction,
                    "interview_results": session.interview_results,
                    "started_at": session.started_at.isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "total_duration_minutes": (datetime.utcnow() - session.started_at).total_seconds() / 60
                }
                
                session.current_stage = OrchestratorStage.COMPLETED
                session.completed_at = datetime.utcnow()
                
                logger.info(f"[{session.session_id}] Interview process completed")
                
                return OrchestratorResponse(
                    session_id=session.session_id,
                    current_stage="completed",
                    message="Interview process completed successfully!",
                    agent_response=final_report if isinstance(final_report, dict) else (final_report.model_dump() if hasattr(final_report, 'model_dump') else {}),
                    next_action="view_report",
                    progress=self._get_progress(session),
                    completed=True
                )
            
            raise ValueError(f"Invalid action for final_report stage: {action}")
            
        except Exception as e:
            logger.error(f"Error in final_report stage: {str(e)}")
            raise
    
    
    def _get_progress(self, session: UnifiedInterviewSession) -> Dict[str, Any]:
        """Calculate progress information."""
        stage_map = {
            OrchestratorStage.GREETING: (1, "Greeting & Info Collection"),
            OrchestratorStage.INFO_COLLECTION: (1, "Greeting & Info Collection"),
            OrchestratorStage.PROFILE_VALIDATION: (2, "Profile Validation"),
            OrchestratorStage.PROJECT_ANALYSIS: (3, "Project Analysis"),
            OrchestratorStage.KPI_EXTRACTION: (4, "KPI Extraction"),
            OrchestratorStage.TECHNICAL_INTERVIEW: (5, "Technical Interview"),
            OrchestratorStage.FINAL_REPORT: (6, "Final Report"),
            OrchestratorStage.COMPLETED: (6, "Completed")
        }
        
        current_num, stage_name = stage_map.get(session.current_stage, (0, "Unknown"))
        
        return {
            "total_stages": 6,
            "completed_stages": current_num - 1 if current_num > 0 else 0,
            "current_stage": current_num,
            "stage_name": stage_name,
            "percentage": int((current_num / 6) * 100)
        }
    
    
    def get_session(self, session_id: str) -> Optional[UnifiedInterviewSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)


# Singleton instance
_orchestrator = None

def get_orchestrator() -> InterviewOrchestrator:
    """Get or create Orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = InterviewOrchestrator()
    return _orchestrator
