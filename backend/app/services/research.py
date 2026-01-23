"""
External research integration for candidate information gathering.
"""
import logging
import httpx
from typing import Optional, List
from ..models import SearchResult
from ..config import get_settings

logger = logging.getLogger(__name__)


async def search_web(query: str, num_results: int = 5) -> List[SearchResult]:
    """
    Search the web using Serper API.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results
    """
    try:
        settings = get_settings()
        
        if not settings.serper_api_key:
            logger.warning("Serper API key not configured")
            return []
        
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": settings.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": num_results
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        
        # Parse results
        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="serper"
                )
            )
        
        logger.info(f"Web search completed: {len(results)} results for '{query}'")
        return results
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error in web search: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        return []


async def get_linkedin_summary(name: str, company: Optional[str] = None) -> Optional[str]:
    """
    Get LinkedIn profile summary for a candidate.
    
    Note: This is a stub implementation. Real implementation would require:
    - LinkedIn API access or scraping (with proper authorization)
    - OAuth authentication
    - Rate limiting
    
    Args:
        name: Candidate's name
        company: Optional company name for better matching
        
    Returns:
        LinkedIn profile summary or None
    """
    # TODO: Implement LinkedIn integration
    # Options:
    # 1. LinkedIn Official API (requires partnership)
    # 2. Web scraping with proper authorization
    # 3. Third-party services like PhantomBuster, Apify
    
    logger.info(f"LinkedIn lookup requested for: {name} at {company}")
    logger.warning("LinkedIn integration not implemented - returning None")
    
    # For now, we can use web search as a fallback
    if company:
        query = f"{name} {company} LinkedIn"
    else:
        query = f"{name} LinkedIn profile"
    
    search_results = await search_web(query, num_results=3)
    
    linkedin_results = [r for r in search_results if "linkedin.com" in r.url.lower()]
    
    if linkedin_results:
        # Return a summary based on search snippets
        summary = f"LinkedIn profile found: {linkedin_results[0].url}\n"
        summary += f"Preview: {linkedin_results[0].snippet}"
        return summary
    
    return None


async def get_github_summary(name_or_handle: str) -> Optional[str]:
    """
    Get GitHub profile summary for a candidate.
    
    This implementation uses GitHub's public API which doesn't require authentication
    for basic profile information.
    
    Args:
        name_or_handle: GitHub username or candidate name
        
    Returns:
        GitHub profile summary or None
    """
    try:
        # Try direct GitHub API lookup
        username = name_or_handle.replace(" ", "").replace("@", "")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get user profile
            user_response = await client.get(
                f"https://api.github.com/users/{username}",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                
                # Get repositories
                repos_response = await client.get(
                    f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10",
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                
                repos_data = repos_response.json() if repos_response.status_code == 200 else []
                
                # Build summary
                summary = f"GitHub Profile: {user_data.get('html_url')}\n"
                summary += f"Name: {user_data.get('name', 'N/A')}\n"
                summary += f"Bio: {user_data.get('bio', 'N/A')}\n"
                summary += f"Public Repos: {user_data.get('public_repos', 0)}\n"
                summary += f"Followers: {user_data.get('followers', 0)}\n"
                summary += f"Following: {user_data.get('following', 0)}\n"
                
                if repos_data and isinstance(repos_data, list):
                    summary += f"\nTop Repositories:\n"
                    for repo in repos_data[:5]:
                        stars = repo.get('stargazers_count', 0)
                        summary += f"- {repo.get('name')} ({repo.get('language', 'N/A')})"
                        if stars > 0:
                            summary += f" ⭐ {stars}"
                        summary += "\n"
                
                logger.info(f"GitHub profile found for: {username}")
                return summary
        
        # If direct lookup fails, try web search
        logger.info(f"Direct GitHub lookup failed for '{username}', trying search")
        search_results = await search_web(f"{name_or_handle} GitHub", num_results=3)
        github_results = [r for r in search_results if "github.com" in r.url.lower()]
        
        if github_results:
            summary = f"GitHub profile found via search: {github_results[0].url}\n"
            summary += f"Preview: {github_results[0].snippet}"
            return summary
        
        return None
        
    except Exception as e:
        logger.error(f"Error in GitHub lookup: {str(e)}")
        return None


async def research_candidate(name: str, email: Optional[str] = None, github: Optional[str] = None) -> dict:
    """
    Comprehensive candidate research across multiple platforms.
    
    Args:
        name: Candidate's name
        email: Optional email address
        github: Optional GitHub username
        
    Returns:
        Dictionary with research results
    """
    logger.info(f"Starting candidate research for: {name}")
    
    results = {
        "name": name,
        "linkedin": None,
        "github": None
    }

    # LinkedIn lookup
    linkedin_summary = await get_linkedin_summary(name)
    if linkedin_summary:
        results["linkedin"] = linkedin_summary

    # GitHub lookup
    if github:
        github_summary = await get_github_summary(github)
        if github_summary:
            results["github"] = github_summary

    logger.info(f"Candidate research completed for: {name}")
    return results


async def research_company(company_name: str) -> dict:
    """
    Research company information.
    
    Args:
        company_name: Company name
        
    Returns:
        Dictionary with company information
    """
    logger.info(f"Starting company research for: {company_name}")
    
    results = {
        "name": company_name,
        "info": []
    }
    
    # Search for company info
    search_results = await search_web(f"{company_name} company about careers", num_results=5)
    results["info"] = [
        {"title": r.title, "url": r.url, "snippet": r.snippet}
        for r in search_results
    ]
    
    logger.info(f"Company research completed for: {company_name}")
    return results
