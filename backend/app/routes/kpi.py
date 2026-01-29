"""
KPI Routes - Endpoints for KPI determination and management.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ..services.kpi_determiner_db import get_kpi_determiner
from database import get_db_stats, list_all_jds, list_all_candidates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/kpi", tags=["kpi"])


# Request/Response Models
class KPIRequest(BaseModel):
    """Request to determine KPIs."""
    jd_id: int
    candidate_id: int


class KPIResponse(BaseModel):
    """Response containing determined KPIs."""
    kpis: List[dict]
    reasoning: str
    candidate_info: dict
    jd_info: dict
    database_ids: dict


class DatabaseInfoResponse(BaseModel):
    """Response with database information."""
    total_jds: int
    total_candidates: int
    jds: List[dict] = []
    candidates: List[dict] = []


@router.get("/database-info")
async def get_database_info(include_data: bool = Query(False)):
    """
    Get information about available JDs and candidates in database.
    
    Args:
        include_data: If True, includes full JD and candidate data
        
    Returns:
        Database statistics and optionally full data
    """
    try:
        stats = get_db_stats()
        
        response = {
            "total_jds": stats["total_jds"],
            "total_candidates": stats["total_candidates"],
            "db_path": stats["db_path"]
        }
        
        if include_data:
            jds = list_all_jds()
            candidates = list_all_candidates()
            
            response["jds"] = [
                {
                    "id": jd["id"],
                    "title": jd["content"].get("job_title", jd.get("title")),
                    "company": jd["content"].get("company", jd.get("company")),
                    "created_at": jd["created_at"]
                }
                for jd in jds
            ]
            
            response["candidates"] = [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "email": c["email"],
                    "created_at": c["created_at"]
                }
                for c in candidates
            ]
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/determine", response_model=KPIResponse)
async def determine_kpis(request: KPIRequest):
    """
    Determine KPIs for a candidate based on job description and CV.
    
    Args:
        request: KPIRequest containing jd_id and candidate_id
        
    Returns:
        KPI determination results with reasoning and scores
    """
    try:
        logger.info(f"Received KPI determination request for JD {request.jd_id}, Candidate {request.candidate_id}")
        
        kpi_determiner = get_kpi_determiner()
        
        # Determine KPIs using Gemini API
        result = await kpi_determiner.determine_kpis_from_db(
            jd_id=request.jd_id,
            candidate_id=request.candidate_id
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in KPI determination: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error determining KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_jobs():
    """Get all job descriptions available in database."""
    try:
        jds = list_all_jds()
        
        return {
            "total": len(jds),
            "jobs": [
                {
                    "id": jd["id"],
                    "title": jd["content"].get("job_title", jd.get("title")),
                    "company": jd["content"].get("company", jd.get("company")),
                    "location": jd["content"].get("location", ""),
                    "experience_required": jd["content"].get("experience_required", ""),
                    "created_at": jd["created_at"]
                }
                for jd in jds
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{jd_id}")
async def get_job_detail(jd_id: int):
    """Get detailed information about a specific job description."""
    try:
        from database import get_jd_by_id
        
        jd = get_jd_by_id(jd_id)
        if not jd:
            raise HTTPException(status_code=404, detail=f"Job description {jd_id} not found")
        
        content = jd.get("content", {})
        
        return {
            "id": jd["id"],
            "title": content.get("job_title"),
            "company": content.get("company"),
            "location": content.get("location"),
            "employment_type": content.get("employment_type"),
            "experience_required": content.get("experience_required"),
            "job_summary": content.get("job_summary"),
            "responsibilities": content.get("responsibilities", []),
            "required_skills": content.get("required_skills", []),
            "preferred_skills": content.get("preferred_skills", []),
            "benefits": content.get("benefits", []),
            "created_at": jd["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates")
async def get_candidates():
    """Get all candidates available in database."""
    try:
        candidates = list_all_candidates()
        
        return {
            "total": len(candidates),
            "candidates": [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "email": c["email"],
                    "created_at": c["created_at"]
                }
                for c in candidates
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates/{candidate_id}")
async def get_candidate_detail(candidate_id: int):
    """Get detailed information about a specific candidate."""
    try:
        from database import get_candidate_by_id
        
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
        
        content = candidate.get("content", {})
        
        return {
            "id": candidate["id"],
            "name": candidate["name"],
            "email": candidate["email"],
            "phone": content.get("phone"),
            "summary": content.get("summary"),
            "skills": content.get("skills", []),
            "experience": content.get("experience", []),
            "education": content.get("education", []),
            "certifications": content.get("certifications", []),
            "projects": content.get("projects", []),
            "created_at": candidate["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
