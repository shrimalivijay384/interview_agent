"""
Interview State Schema for LangGraph

This module defines the state structure that flows through the interview graph.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
import operator


class InterviewState(TypedDict, total=False):
    """
    Central state for the interview agent graph.
    
    This state is passed between all nodes and updated throughout the interview.
    """
    
    # Session Metadata
    session_id: str
    created_at: str
    updated_at: str
    status: str  # 'active', 'completed', 'paused', 'error'
    
    # Input Data
    cv_text: str
    jd_text: str
    resume_id: Optional[str]
    
    # Current Stage
    current_stage: str  # 'greeting', 'info_collection', 'profile_validation', etc.
    completed_stages: Annotated[List[str], operator.add]  # Accumulate completed stages
    
    # Collected Information
    candidate_info: Dict[str, Any]  # Name, role, experience, tech_stack, location
    profile_urls: Dict[str, str]  # linkedin, github
    
    # Agent Outputs
    greeting_data: Optional[Dict[str, Any]]
    info_collection_data: Optional[Dict[str, Any]]
    profile_validation_data: Optional[Dict[str, Any]]
    project_analysis_data: Optional[Dict[str, Any]]
    kpi_interview_data: Optional[Dict[str, Any]]
    
    # Conversation History
    messages: Annotated[List[Dict[str, str]], operator.add]  # [{"role": "agent", "content": "..."}]
    
    # User Interaction
    waiting_for_input: bool
    current_question: Optional[str]
    user_response: Optional[str]
    
    # Validation Results
    linkedin_verified: bool
    github_verified: bool
    profile_consistency: Dict[str, Any]
    
    # Project Analysis
    projects: List[Dict[str, Any]]
    current_project_index: int
    project_deep_dive_complete: bool
    
    # KPI Assessment
    extracted_kpis: List[Dict[str, Any]]
    kpi_scores: Dict[str, int]
    technical_questions: List[Dict[str, Any]]
    current_question_index: int
    
    # Final Results
    overall_score: Optional[int]
    strengths: List[str]
    weaknesses: List[str]
    recommendation: Optional[str]  # 'strong_yes', 'yes', 'maybe', 'no'
    final_report: Optional[Dict[str, Any]]
    
    # Error Handling
    errors: Annotated[List[str], operator.add]
    retry_count: int
    
    # RAG Context (optional)
    similar_candidates: Optional[List[Dict[str, Any]]]
    relevant_questions: Optional[List[Dict[str, Any]]]
    company_context: Optional[List[Dict[str, Any]]]


class NodeOutput(TypedDict, total=False):
    """Output format for graph nodes"""
    stage_complete: bool
    next_stage: Optional[str]
    data: Dict[str, Any]
    message: Optional[str]
    error: Optional[str]


def create_initial_state(
    cv_text: str,
    jd_text: str,
    session_id: str,
    resume_id: Optional[str] = None
) -> InterviewState:
    """
    Create initial interview state
    
    Args:
        cv_text: Candidate's CV text
        jd_text: Job description text
        session_id: Unique session identifier
        resume_id: Optional resume ID
    
    Returns:
        Initial interview state
    """
    return InterviewState(
        # Session metadata
        session_id=session_id,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        status='active',
        
        # Input data
        cv_text=cv_text,
        jd_text=jd_text,
        resume_id=resume_id,
        
        # Current stage
        current_stage='greeting',
        completed_stages=[],
        
        # Collected information
        candidate_info={},
        profile_urls={},
        
        # Agent outputs
        greeting_data=None,
        info_collection_data=None,
        profile_validation_data=None,
        project_analysis_data=None,
        kpi_interview_data=None,
        
        # Conversation
        messages=[],
        
        # User interaction
        waiting_for_input=False,
        current_question=None,
        user_response=None,
        
        # Validation
        linkedin_verified=False,
        github_verified=False,
        profile_consistency={},
        
        # Projects
        projects=[],
        current_project_index=0,
        project_deep_dive_complete=False,
        
        # KPIs
        extracted_kpis=[],
        kpi_scores={},
        technical_questions=[],
        current_question_index=0,
        
        # Results
        overall_score=None,
        strengths=[],
        weaknesses=[],
        recommendation=None,
        final_report=None,
        
        # Error handling
        errors=[],
        retry_count=0,
        
        # RAG context
        similar_candidates=None,
        relevant_questions=None,
        company_context=None
    )


def update_state(
    state: InterviewState,
    updates: Dict[str, Any]
) -> InterviewState:
    """
    Update interview state with new values
    
    Args:
        state: Current state
        updates: Dictionary of updates
    
    Returns:
        Updated state
    """
    updated = state.copy()
    updated.update(updates)
    updated['updated_at'] = datetime.utcnow().isoformat()
    return updated
