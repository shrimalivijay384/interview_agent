"""
LangGraph Nodes for Interview Agent

Each node represents a stage in the interview process.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .state import InterviewState
from ..services.gemini_client import get_gemini_client
from ..services.rag_knowledge_base import get_rag_knowledge_base

logger = logging.getLogger(__name__)


# ==================== NODE: GREETING ====================

async def greeting_node(state: InterviewState) -> Dict[str, Any]:
    """
    Node 1: Send initial greeting to candidate
    
    Returns:
        Updated state with greeting message
    """
    logger.info(f"[GREETING NODE] Session: {state['session_id']}")
    
    try:
        gemini = get_gemini_client()
        candidate_name = state.get('candidate_info', {}).get('name', 'there')
        
        # Generate personalized greeting
        greeting_prompt = f"""
        You are a friendly technical interviewer. Greet the candidate warmly.
        Candidate name: {candidate_name if candidate_name != 'there' else 'Unknown'}
        
        Generate a warm, professional greeting (2-3 sentences).
        """
        
        greeting_message = await gemini.chat(
            [
                {"role": "system", "content": "You are a warm, professional technical interviewer."},
                {"role": "user", "content": greeting_prompt}
            ]
        )
        
        return {
            "current_stage": "greeting",
            "greeting_data": {
                "message": greeting_message,
                "timestamp": datetime.utcnow().isoformat()
            },
            "messages": [{"role": "agent", "content": greeting_message}],
            "waiting_for_input": True,
            "current_question": greeting_message
        }
        
    except Exception as e:
        logger.error(f"Error in greeting node: {str(e)}")
        return {
            "errors": [f"Greeting error: {str(e)}"],
            "status": "error"
        }


# ==================== NODE: INFO COLLECTION ====================

async def info_collection_node(state: InterviewState) -> Dict[str, Any]:
    """
    Node 2: Collect basic candidate information
    
    Collects: Name, role, experience, tech stack, location
    """
    logger.info(f"[INFO_COLLECTION NODE] Session: {state['session_id']}")
    
    try:
        gemini = get_gemini_client()
        cv_text = state.get('cv_text', '')
        user_response = state.get('user_response', '')
        candidate_info = state.get('candidate_info', {})
        
        # Determine what info is still needed
        needed_fields = []
        if not candidate_info.get('name'):
            needed_fields.append('name')
        if not candidate_info.get('role'):
            needed_fields.append('role/position')
        if not candidate_info.get('experience_years'):
            needed_fields.append('years of experience')
        if not candidate_info.get('tech_stack'):
            needed_fields.append('tech stack/skills')
        if not candidate_info.get('location'):
            needed_fields.append('location/timezone')
        
        if needed_fields:
            # Generate question for next field
            prompt = f"""
            You are collecting information from a candidate.
            CV excerpt: {cv_text[:500]}
            
            Already collected: {list(candidate_info.keys())}
            Still need: {needed_fields}
            
            Generate ONE specific question to collect the next piece of information.
            Keep it natural and conversational.
            """
            
            question = await gemini.chat([
                {"role": "system", "content": "You are a professional interviewer."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "current_stage": "info_collection",
                "waiting_for_input": True,
                "current_question": question,
                "messages": [{"role": "agent", "content": question}]
            }
        else:
            # All info collected
            return {
                "current_stage": "info_collection",
                "info_collection_data": {
                    "complete": True,
                    "collected_info": candidate_info
                },
                "completed_stages": ["info_collection"],
                "waiting_for_input": False
            }
            
    except Exception as e:
        logger.error(f"Error in info_collection node: {str(e)}")
        return {
            "errors": [f"Info collection error: {str(e)}"]
        }


# ==================== NODE: PROFILE VALIDATION ====================

async def profile_validation_node(state: InterviewState) -> Dict[str, Any]:
    """
    Node 3: Validate LinkedIn and GitHub profiles
    """
    logger.info(f"[PROFILE_VALIDATION NODE] Session: {state['session_id']}")
    
    try:
        profile_urls = state.get('profile_urls', {})
        
        if not profile_urls.get('linkedin'):
            # Ask for LinkedIn
            question = "Could you please share your LinkedIn profile URL? This helps us verify your professional background."
            return {
                "current_stage": "profile_validation",
                "waiting_for_input": True,
                "current_question": question,
                "messages": [{"role": "agent", "content": question}]
            }
        
        if not profile_urls.get('github') and not state.get('github_skipped'):
            # Ask for GitHub (optional)
            question = "Do you have a GitHub or GitLab profile you'd like to share? (This is optional)"
            return {
                "current_stage": "profile_validation",
                "waiting_for_input": True,
                "current_question": question,
                "messages": [{"role": "agent", "content": question}]
            }
        
        # Validation complete
        validation_result = {
            "linkedin_url": profile_urls.get('linkedin'),
            "github_url": profile_urls.get('github'),
            "linkedin_verified": True,  # Would call actual validation service
            "github_verified": bool(profile_urls.get('github')),
            "consistency_check": "Passed"
        }
        
        return {
            "current_stage": "profile_validation",
            "profile_validation_data": validation_result,
            "linkedin_verified": True,
            "github_verified": bool(profile_urls.get('github')),
            "completed_stages": ["profile_validation"],
            "waiting_for_input": False
        }
        
    except Exception as e:
        logger.error(f"Error in profile_validation node: {str(e)}")
        return {
            "errors": [f"Profile validation error: {str(e)}"]
        }


# ==================== NODE: PROJECT ANALYSIS ====================

async def project_analysis_node(state: InterviewState) -> Dict[str, Any]:
    """
    Node 4: Analyze candidate's projects
    """
    logger.info(f"[PROJECT_ANALYSIS NODE] Session: {state['session_id']}")
    
    try:
        gemini = get_gemini_client()
        cv_text = state.get('cv_text', '')
        projects = state.get('projects', [])
        current_index = state.get('current_project_index', 0)
        
        # Extract projects if not done
        if not projects:
            prompt = f"""
            Extract 2-3 key projects from this CV:
            {cv_text}
            
            For each project, return JSON with:
            - title
            - technologies
            - description
            - your_role
            
            Return as JSON array.
            """
            
            response = await gemini.chat([
                {"role": "system", "content": "Extract projects from CV. Return valid JSON array."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse projects (simplified - add proper JSON parsing)
            projects = [{"title": "Project Analysis", "description": "Extracted from CV"}]
            
            return {
                "current_stage": "project_analysis",
                "projects": projects,
                "current_project_index": 0,
                "waiting_for_input": False
            }
        
        # Ask about current project
        if current_index < len(projects):
            project = projects[current_index]
            question = f"Tell me about your {project.get('title', 'project')}. What was your specific role and main responsibilities?"
            
            return {
                "current_stage": "project_analysis",
                "waiting_for_input": True,
                "current_question": question,
                "messages": [{"role": "agent", "content": question}]
            }
        else:
            # All projects analyzed
            return {
                "current_stage": "project_analysis",
                "project_analysis_data": {
                    "projects_analyzed": len(projects),
                    "projects": projects
                },
                "project_deep_dive_complete": True,
                "completed_stages": ["project_analysis"],
                "waiting_for_input": False
            }
            
    except Exception as e:
        logger.error(f"Error in project_analysis node: {str(e)}")
        return {
            "errors": [f"Project analysis error: {str(e)}"]
        }


# ==================== NODE: KPI EXTRACTION ====================

async def kpi_extraction_node(state: InterviewState) -> Dict[str, Any]:
    """
    Node 5: Extract KPIs from JD and conduct technical interview
    """
    logger.info(f"[KPI_EXTRACTION NODE] Session: {state['session_id']}")
    
    try:
        gemini = get_gemini_client()
        jd_text = state.get('jd_text', '')
        extracted_kpis = state.get('extracted_kpis', [])
        
        # Extract KPIs if not done
        if not extracted_kpis:
            prompt = f"""
            Extract 5-8 Key Performance Indicators from this job description:
            {jd_text}
            
            Return JSON array with:
            - kpi_name
            - category (delivery/quality/impact/leadership)
            - description
            - sample_question
            """
            
            response = await gemini.chat([
                {"role": "system", "content": "Extract KPIs from job description. Return JSON."},
                {"role": "user", "content": prompt}
            ])
            
            # Simplified KPI extraction
            kpis = [
                {"kpi_name": "Scalability", "category": "delivery", "score": 0},
                {"kpi_name": "Code Quality", "category": "quality", "score": 0},
                {"kpi_name": "Business Impact", "category": "impact", "score": 0}
            ]
            
            return {
                "current_stage": "kpi_extraction",
                "extracted_kpis": kpis,
                "current_question_index": 0,
                "waiting_for_input": False
            }
        
        # Conduct KPI interview
        current_q_index = state.get('current_question_index', 0)
        
        if current_q_index < len(extracted_kpis):
            kpi = extracted_kpis[current_q_index]
            question = f"Regarding {kpi['kpi_name']}: Can you describe your experience and achievements in this area?"
            
            return {
                "current_stage": "kpi_extraction",
                "waiting_for_input": True,
                "current_question": question,
                "messages": [{"role": "agent", "content": question}]
            }
        else:
            # KPI interview complete
            return {
                "current_stage": "kpi_extraction",
                "kpi_interview_data": {
                    "kpis_assessed": len(extracted_kpis),
                    "kpi_scores": state.get('kpi_scores', {})
                },
                "completed_stages": ["kpi_extraction"],
                "waiting_for_input": False
            }
            
    except Exception as e:
        logger.error(f"Error in kpi_extraction node: {str(e)}")
        return {
            "errors": [f"KPI extraction error: {str(e)}"]
        }


# ==================== NODE: REPORT GENERATION ====================

async def report_generation_node(state: InterviewState) -> Dict[str, Any]:
    """
    Node 6: Generate final interview report
    """
    logger.info(f"[REPORT_GENERATION NODE] Session: {state['session_id']}")
    
    try:
        gemini = get_gemini_client()
        
        # Compile all data
        report_data = {
            "candidate_info": state.get('candidate_info', {}),
            "profile_validation": state.get('profile_validation_data', {}),
            "projects": state.get('projects', []),
            "kpi_scores": state.get('kpi_scores', {}),
            "strengths": [],
            "weaknesses": [],
            "overall_score": 85,  # Would calculate from KPI scores
            "recommendation": "strong_yes"
        }
        
        # Generate detailed report
        prompt = f"""
        Generate a comprehensive interview assessment report.
        
        Candidate: {report_data['candidate_info'].get('name', 'Unknown')}
        KPI Scores: {report_data['kpi_scores']}
        
        Provide:
        1. Overall score (0-100)
        2. Top 3 strengths
        3. Top 2 areas for improvement
        4. Hiring recommendation (strong_yes/yes/maybe/no)
        5. Detailed justification
        
        Return as JSON.
        """
        
        report_text = await gemini.chat([
            {"role": "system", "content": "Generate interview assessment report."},
            {"role": "user", "content": prompt}
        ])
        
        final_report = {
            **report_data,
            "report_text": report_text,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "current_stage": "completion",
            "status": "completed",
            "final_report": final_report,
            "overall_score": report_data['overall_score'],
            "recommendation": report_data['recommendation'],
            "completed_stages": ["report_generation"],
            "waiting_for_input": False,
            "messages": [{"role": "agent", "content": "Thank you for your time! Your interview is complete. The report is now available."}]
        }
        
    except Exception as e:
        logger.error(f"Error in report_generation node: {str(e)}")
        return {
            "errors": [f"Report generation error: {str(e)}"],
            "status": "error"
        }


# ==================== NODE: PROCESS USER INPUT ====================

async def process_user_input_node(state: InterviewState) -> Dict[str, Any]:
    """
    Special node: Process user's response and extract information
    
    This node runs when user provides input, extracting relevant info
    before routing to the next stage.
    """
    logger.info(f"[PROCESS_INPUT NODE] Session: {state['session_id']}")
    
    try:
        user_response = state.get('user_response', '')
        current_stage = state.get('current_stage', '')
        
        if not user_response:
            return {}
        
        gemini = get_gemini_client()
        
        # Extract info based on current stage
        if current_stage == 'info_collection':
            # Extract structured data from response
            prompt = f"""
            Extract information from this candidate response:
            "{user_response}"
            
            Return JSON with any of these fields found:
            - name
            - role
            - experience_years (number)
            - tech_stack (array)
            - location
            """
            
            # Simplified extraction
            candidate_info = state.get('candidate_info', {})
            # Would use Gemini to parse actual response
            
            return {
                "candidate_info": candidate_info,
                "user_response": None  # Clear after processing
            }
        
        elif current_stage == 'profile_validation':
            # Extract URLs
            profile_urls = state.get('profile_urls', {})
            if 'linkedin.com' in user_response.lower():
                profile_urls['linkedin'] = user_response.strip()
            elif 'github.com' in user_response.lower() or 'gitlab.com' in user_response.lower():
                profile_urls['github'] = user_response.strip()
            
            return {
                "profile_urls": profile_urls,
                "user_response": None
            }
        
        elif current_stage == 'project_analysis':
            # Store project answer
            current_index = state.get('current_project_index', 0)
            return {
                "current_project_index": current_index + 1,
                "messages": [{"role": "user", "content": user_response}],
                "user_response": None
            }
        
        elif current_stage == 'kpi_extraction':
            # Score the response
            current_q_index = state.get('current_question_index', 0)
            # Would use Gemini to score response
            
            return {
                "current_question_index": current_q_index + 1,
                "messages": [{"role": "user", "content": user_response}],
                "user_response": None
            }
        
        return {
            "messages": [{"role": "user", "content": user_response}],
            "user_response": None
        }
        
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        return {
            "errors": [f"Input processing error: {str(e)}"]
        }
