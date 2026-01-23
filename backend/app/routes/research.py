"""
Web Research routes - LinkedIn, GitHub, and general web search.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..services.research import (
    search_web, get_linkedin_summary, get_github_summary,
    research_candidate, research_company
)
from ..models import SearchResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/research", tags=["research"])


# Request/Response Models
class WebSearchRequest(BaseModel):
    """Request for web search."""
    query: str
    num_results: int = 5


class LinkedInSearchRequest(BaseModel):
    """Request for LinkedIn profile lookup."""
    name: str
    company: Optional[str] = None


class GitHubSearchRequest(BaseModel):
    """Request for GitHub profile lookup."""
    username_or_name: str


class CandidateResearchRequest(BaseModel):
    """Request for comprehensive candidate research."""
    name: str
    email: Optional[str] = None
    github: Optional[str] = None


class CompanyResearchRequest(BaseModel):
    """Request for company research."""
    company_name: str


class ResearchResponse(BaseModel):
    """Response for research queries."""
    success: bool
    data: dict
    error: Optional[str] = None


# Endpoints
@router.post("/web-search")
async def web_search(request: WebSearchRequest) -> ResearchResponse:
    """
    Perform a general web search using Serper API.
    
    Args:
        request: Search query and number of results
        
    Returns:
        List of search results
    """
    try:
        if not request.query or len(request.query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        results = await search_web(request.query, num_results=min(request.num_results, 10))
        
        logger.info(f"Web search: '{request.query}' returned {len(results)} results")
        return ResearchResponse(
            success=True,
            data={"query": request.query, "results": [r.dict() for r in results]}
        )
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/linkedin")
async def linkedin_search(request: LinkedInSearchRequest) -> ResearchResponse:
    """
    Search for LinkedIn profile information.
    
    Uses Serper API to find LinkedIn profiles and extract profile information.
    
    Args:
        request: Candidate name and optional company
        
    Returns:
        LinkedIn profile summary
    """
    try:
        if not request.name or len(request.name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
        
        linkedin_summary = await get_linkedin_summary(request.name, request.company)
        
        if linkedin_summary:
            logger.info(f"LinkedIn profile found for: {request.name}")
            return ResearchResponse(
                success=True,
                data={
                    "name": request.name,
                    "company": request.company,
                    "profile_summary": linkedin_summary
                }
            )
        else:
            logger.warning(f"No LinkedIn profile found for: {request.name}")
            return ResearchResponse(
                success=True,
                data={
                    "name": request.name,
                    "company": request.company,
                    "profile_summary": None,
                    "message": "No LinkedIn profile found"
                }
            )
    except Exception as e:
        logger.error(f"Error in LinkedIn search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LinkedIn search failed: {str(e)}")


@router.post("/github")
async def github_search(request: GitHubSearchRequest) -> ResearchResponse:
    """
    Search for GitHub profile information.
    
    Uses GitHub API for direct lookups, falls back to Serper API if needed.
    Returns public profile information including repositories, followers, etc.
    
    Args:
        request: GitHub username or candidate name
        
    Returns:
        GitHub profile summary with repository information
    """
    try:
        if not request.username_or_name or len(request.username_or_name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Username/name must be at least 2 characters")
        
        github_summary = await get_github_summary(request.username_or_name)
        
        if github_summary:
            logger.info(f"GitHub profile found for: {request.username_or_name}")
            return ResearchResponse(
                success=True,
                data={
                    "username": request.username_or_name,
                    "profile_summary": github_summary
                }
            )
        else:
            logger.warning(f"No GitHub profile found for: {request.username_or_name}")
            return ResearchResponse(
                success=True,
                data={
                    "username": request.username_or_name,
                    "profile_summary": None,
                    "message": "No GitHub profile found"
                }
            )
    except Exception as e:
        logger.error(f"Error in GitHub search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GitHub search failed: {str(e)}")


@router.post("/candidate")
async def research_candidate_endpoint(request: CandidateResearchRequest) -> ResearchResponse:
    """
    Comprehensive candidate research across multiple platforms.
    
    Searches for the candidate across:
    - LinkedIn profile
    - GitHub profile (if username provided)
    - General web presence
    
    Args:
        request: Candidate name, email, and optional GitHub username
        
    Returns:
        Consolidated research results
    """
    try:
        if not request.name or len(request.name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Candidate name must be at least 2 characters")
        
        results = await research_candidate(request.name, request.email, request.github)
        
        logger.info(f"Candidate research completed for: {request.name}")
        return ResearchResponse(
            success=True,
            data=results
        )
    except Exception as e:
        logger.error(f"Error in candidate research: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Candidate research failed: {str(e)}")


@router.post("/company")
async def research_company_endpoint(request: CompanyResearchRequest) -> ResearchResponse:
    """
    Research company information.
    
    Searches for company information including:
    - About page
    - Career page
    - General company information
    
    Args:
        request: Company name
        
    Returns:
        Company research results
    """
    try:
        if not request.company_name or len(request.company_name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Company name must be at least 2 characters")
        
        results = await research_company(request.company_name)
        
        logger.info(f"Company research completed for: {request.company_name}")
        return ResearchResponse(
            success=True,
            data=results
        )
    except Exception as e:
        logger.error(f"Error in company research: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Company research failed: {str(e)}")


@router.get("/status")
async def research_status() -> ResearchResponse:
    """
    Check research service status and API key configuration.
    
    Returns:
        Status of research service
    """
    from ..config import get_settings
    settings = get_settings()
    
    serper_configured = bool(settings.serper_api_key)
    
    return ResearchResponse(
        success=True,
        data={
            "service": "web-research",
            "status": "operational",
            "apis": {
                "serper": serper_configured,
                "github": True  # GitHub API always available
            },
            "features": [
                "web_search",
                "linkedin_lookup",
                "github_lookup",
                "candidate_research",
                "company_research"
            ]
        }
    )
