"""
Resume/CV parsing service using Gemini.
"""
import logging
from app.models import Resume, WorkExperienceItem, EducationItem, ProjectItem
from app.services.gemini_client import get_gemini_client
from typing import Dict, Any

logger = logging.getLogger(__name__)


RESUME_PARSING_SYSTEM_PROMPT = """You are an expert resume/CV parser. Your task is to extract structured information from resumes and return it in JSON format.

You must extract the following information:
- name: Candidate's full name (required)
- email: Email address (if available)
- phone: Phone number (if available)
- linkedin: LinkedIn profile URL (if available)
- github: GitHub profile URL (if available)
- summary: Professional summary or objective (if available)
- skills: List of technical and soft skills
- work_experience: List of work experiences with:
  - company: Company name
  - title: Job title
  - start_date: Start date (any format)
  - end_date: End date or "Present"
  - description: Job description
  - achievements: List of key achievements
  - technologies: Technologies used
- education: List of education entries with:
  - institution: School/University name
  - degree: Degree type (BS, MS, PhD, etc.)
  - field_of_study: Major/field
  - start_date: Start date
  - end_date: End date
  - gpa: GPA if mentioned
  - achievements: Academic achievements
- projects: List of projects with:
  - name: Project name
  - description: Project description
  - technologies: Technologies used
  - url: Project URL if available
  - role: Candidate's role
  - achievements: Key achievements
- certifications: List of certifications
- languages: List of languages spoken

Be thorough and extract as much information as possible. If a field is not found, omit it or use an empty list/null."""


async def parse_resume(text: str) -> Resume:
    """
    Parse resume text into structured Resume object.
    
    Args:
        text: Raw resume text
        
    Returns:
        Parsed Resume object
    """
    try:
        logger.info("Starting resume parsing")
        
        gemini = get_gemini_client()
        
        user_prompt = f"""Parse the following resume and return the information in this exact JSON structure:

{{
  "name": "string",
  "email": "string or null",
  "phone": "string or null",
  "linkedin": "string or null",
  "github": "string or null",
  "summary": "string or null",
  "skills": ["skill1", "skill2"],
  "work_experience": [
    {{
      "company": "string",
      "title": "string",
      "start_date": "string or null",
      "end_date": "string or null",
      "description": "string or null",
      "achievements": ["achievement1"],
      "technologies": ["tech1"]
    }}
  ],
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "field_of_study": "string or null",
      "start_date": "string or null",
      "end_date": "string or null",
      "gpa": "string or null",
      "achievements": ["achievement1"]
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["tech1"],
      "url": "string or null",
      "role": "string or null",
      "achievements": ["achievement1"]
    }}
  ],
  "certifications": ["cert1"],
  "languages": ["language1"]
}}

Resume text:
{text}"""
        
        # Get JSON response from Gemini
        result = await gemini.chat_with_json_response(
            system_prompt=RESUME_PARSING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3  # Lower temperature for more consistent parsing
        )
        
        # Validate and create Resume object
        resume = Resume(**result)
        
        logger.info(f"Successfully parsed resume for: {resume.name}")
        return resume
        
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise ValueError(f"Failed to parse resume: {str(e)}")


async def extract_resume_highlights(resume: Resume) -> Dict[str, Any]:
    """
    Extract key highlights from a parsed resume for quick assessment.
    
    Args:
        resume: Parsed Resume object
        
    Returns:
        Dictionary with key highlights
    """
    total_experience_years = len(resume.work_experience)  # Simplified
    
    all_technologies = set()
    for exp in resume.work_experience:
        all_technologies.update(exp.technologies)
    for proj in resume.projects:
        all_technologies.update(proj.technologies)
    
    return {
        "name": resume.name,
        "total_positions": len(resume.work_experience),
        "estimated_experience_years": total_experience_years,
        "unique_technologies": list(all_technologies),
        "education_level": resume.education[0].degree if resume.education else "Not specified",
        "has_projects": len(resume.projects) > 0,
        "certifications_count": len(resume.certifications),
        "key_skills": resume.skills[:10]  # Top 10 skills
    }
