"""
Job Description parsing service using Gemini.
"""
import logging
from ..models import JobDescription, RequiredSkill, ExperienceLevel
from .gemini_client import get_gemini_client
from typing import Dict, Any

logger = logging.getLogger(__name__)


JD_PARSING_SYSTEM_PROMPT = """You are an expert job description parser. Your task is to extract structured information from job descriptions and return it in JSON format.

You must extract the following information:
- title: Job title (required)
- company: Company name (if available)
- location: Job location (if available)
- employment_type: Type (Full-time, Part-time, Contract, etc.)
- description: Main job description text
- responsibilities: List of key responsibilities
- required_skills: List of required skills with their details:
  - name: Skill name
  - level: Experience level (junior, mid, senior, expert)
  - is_required: Whether it's required (true) or preferred (false)
- preferred_skills: List of preferred/nice-to-have skills
- experience_required: Years of experience required (e.g., "3-5 years")
- education_required: Education requirements
- benefits: List of benefits offered

Be thorough and extract as much information as possible."""


async def parse_jd(text: str) -> JobDescription:
    """
    Parse job description text into structured JobDescription object.
    
    Args:
        text: Raw job description text
        
    Returns:
        Parsed JobDescription object
    """
    try:
        logger.info("Starting job description parsing")
        
        gemini = get_gemini_client()
        
        user_prompt = f"""Parse the following job description and return the information in this exact JSON structure:

{{
  "title": "string",
  "company": "string or null",
  "location": "string or null",
  "employment_type": "string or null",
  "description": "string",
  "responsibilities": ["responsibility1", "responsibility2"],
  "required_skills": [
    {{
      "name": "string",
      "level": "junior|mid|senior|expert",
      "is_required": true
    }}
  ],
  "preferred_skills": ["skill1", "skill2"],
  "experience_required": "string or null",
  "education_required": "string or null",
  "benefits": ["benefit1", "benefit2"]
}}

For the level field in required_skills, use:
- "junior" for entry-level or 0-2 years
- "mid" for intermediate or 2-5 years
- "senior" for senior-level or 5+ years
- "expert" for expert/principal or 8+ years

Job Description:
{text}"""
        
        # Get JSON response from Gemini
        result = await gemini.chat_with_json_response(
            system_prompt=JD_PARSING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3  # Lower temperature for more consistent parsing
        )
        
        # Validate and create JobDescription object
        jd = JobDescription(**result)
        
        logger.info(f"Successfully parsed job description: {jd.title}")
        return jd
        
    except Exception as e:
        logger.error(f"Error parsing job description: {str(e)}")
        raise ValueError(f"Failed to parse job description: {str(e)}")


async def extract_jd_highlights(jd: JobDescription) -> Dict[str, Any]:
    """
    Extract key highlights from a parsed job description.
    
    Args:
        jd: Parsed JobDescription object
        
    Returns:
        Dictionary with key highlights
    """
    required_skill_names = [skill.name for skill in jd.required_skills if skill.is_required]
    
    return {
        "title": jd.title,
        "company": jd.company,
        "total_required_skills": len([s for s in jd.required_skills if s.is_required]),
        "total_preferred_skills": len(jd.preferred_skills) + len([s for s in jd.required_skills if not s.is_required]),
        "key_responsibilities_count": len(jd.responsibilities),
        "experience_level": jd.experience_required,
        "top_skills": required_skill_names[:10]
    }
