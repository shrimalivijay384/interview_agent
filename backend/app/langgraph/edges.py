"""
Conditional Edges for LangGraph Interview Flow

Edges determine the routing between nodes based on state.
"""

import logging
from typing import Literal
from .state import InterviewState

logger = logging.getLogger(__name__)


def route_after_greeting(
    state: InterviewState
) -> Literal["info_collection", "end"]:
    """
    Route after greeting node
    
    Returns:
        Next node name or 'end'
    """
    if state.get('status') == 'error':
        return "end"
    
    # Wait for user response, then move to info collection
    if state.get('user_response'):
        return "info_collection"
    
    return "end"  # Waiting for user input


def route_after_info_collection(
    state: InterviewState
) -> Literal["profile_validation", "info_collection", "end"]:
    """
    Route after info collection node
    
    Continues collecting if info incomplete, otherwise moves to profile validation
    """
    if state.get('status') == 'error':
        return "end"
    
    # Check if all required info is collected
    candidate_info = state.get('candidate_info', {})
    required_fields = ['name', 'role', 'experience_years', 'tech_stack', 'location']
    
    has_all_info = all(candidate_info.get(field) for field in required_fields)
    
    if has_all_info:
        logger.info("[ROUTING] All info collected, moving to profile validation")
        return "profile_validation"
    else:
        logger.info(f"[ROUTING] Still need info, staying in info_collection")
        return "info_collection"


def route_after_profile_validation(
    state: InterviewState
) -> Literal["project_analysis", "profile_validation", "end"]:
    """
    Route after profile validation
    
    Continues until LinkedIn is validated, then moves to project analysis
    """
    if state.get('status') == 'error':
        return "end"
    
    # Check if LinkedIn is provided (required)
    profile_urls = state.get('profile_urls', {})
    linkedin_verified = state.get('linkedin_verified', False)
    
    if linkedin_verified or profile_urls.get('linkedin'):
        logger.info("[ROUTING] Profile validated, moving to project analysis")
        return "project_analysis"
    else:
        logger.info("[ROUTING] Still need profile validation")
        return "profile_validation"


def route_after_project_analysis(
    state: InterviewState
) -> Literal["kpi_extraction", "project_analysis", "end"]:
    """
    Route after project analysis
    
    Continues until all projects analyzed, then moves to KPI extraction
    """
    if state.get('status') == 'error':
        return "end"
    
    projects = state.get('projects', [])
    current_index = state.get('current_project_index', 0)
    project_complete = state.get('project_deep_dive_complete', False)
    
    if project_complete or (projects and current_index >= len(projects)):
        logger.info("[ROUTING] Project analysis complete, moving to KPI extraction")
        return "kpi_extraction"
    else:
        logger.info(f"[ROUTING] Continuing project analysis ({current_index}/{len(projects)})")
        return "project_analysis"


def route_after_kpi_extraction(
    state: InterviewState
) -> Literal["report_generation", "kpi_extraction", "end"]:
    """
    Route after KPI extraction
    
    Continues until all KPIs assessed, then generates report
    """
    if state.get('status') == 'error':
        return "end"
    
    extracted_kpis = state.get('extracted_kpis', [])
    current_q_index = state.get('current_question_index', 0)
    
    if extracted_kpis and current_q_index >= len(extracted_kpis):
        logger.info("[ROUTING] KPI interview complete, generating report")
        return "report_generation"
    else:
        logger.info(f"[ROUTING] Continuing KPI assessment ({current_q_index}/{len(extracted_kpis)})")
        return "kpi_extraction"


def route_after_report_generation(
    state: InterviewState
) -> Literal["end"]:
    """
    Route after report generation
    
    Always ends after report is generated
    """
    logger.info("[ROUTING] Interview complete, ending")
    return "end"


def route_user_input(
    state: InterviewState
) -> Literal["greeting", "info_collection", "profile_validation", "project_analysis", "kpi_extraction", "end"]:
    """
    Route after processing user input
    
    Returns to the current stage to continue processing
    """
    current_stage = state.get('current_stage', 'greeting')
    
    if state.get('status') == 'error':
        return "end"
    
    # Return to current stage after processing input
    stage_mapping = {
        'greeting': 'info_collection',
        'info_collection': 'info_collection',
        'profile_validation': 'profile_validation',
        'project_analysis': 'project_analysis',
        'kpi_extraction': 'kpi_extraction'
    }
    
    next_node = stage_mapping.get(current_stage, 'end')
    logger.info(f"[ROUTING] After user input, routing to: {next_node}")
    
    return next_node


def should_continue(
    state: InterviewState
) -> Literal["continue", "end"]:
    """
    Master routing function - decides if interview should continue
    
    Returns:
        'continue' to keep going, 'end' to stop
    """
    status = state.get('status', 'active')
    waiting = state.get('waiting_for_input', False)
    completed = 'report_generation' in state.get('completed_stages', [])
    
    if status == 'error':
        logger.info("[ROUTING] Error status, ending")
        return "end"
    
    if status == 'completed' or completed:
        logger.info("[ROUTING] Interview completed, ending")
        return "end"
    
    if waiting:
        logger.info("[ROUTING] Waiting for user input, pausing")
        return "end"  # Pause execution until user responds
    
    logger.info("[ROUTING] Continuing interview")
    return "continue"


def route_by_stage(
    state: InterviewState
) -> Literal["greeting", "info_collection", "profile_validation", "project_analysis", "kpi_extraction", "report_generation", "end"]:
    """
    Main routing function based on current stage
    
    Used for conditional edges in the graph
    """
    current_stage = state.get('current_stage', 'greeting')
    status = state.get('status', 'active')
    
    if status in ['error', 'completed']:
        return "end"
    
    # Map stages to nodes
    stage_to_node = {
        'greeting': 'greeting',
        'info_collection': 'info_collection',
        'profile_validation': 'profile_validation',
        'project_analysis': 'project_analysis',
        'kpi_extraction': 'kpi_extraction',
        'completion': 'report_generation'
    }
    
    next_node = stage_to_node.get(current_stage, 'end')
    logger.info(f"[ROUTING] Current stage: {current_stage}, routing to: {next_node}")
    
    return next_node
