"""
Service to generate Job Description based on CV/Resume
"""
import logging
from typing import Dict, Any
from .gemini_client import get_gemini_client

logger = logging.getLogger(__name__)


JD_GENERATION_PROMPT = """You are an expert recruiter and job description writer. Based on the provided candidate's CV/Resume, generate a suitable job description that matches their skills, experience level, and career trajectory.

The job description should:
1. Match the candidate's current experience level and skills
2. Be challenging but achievable (slightly above their current level)
3. Align with their career interests and domain
4. Include realistic requirements and responsibilities
5. Be professional and comprehensive

Return the job description in a structured format with:
- Job Title
- Company Type (e.g., "Tech Startup", "Enterprise Software Company", "Consulting Firm")
- Location (can be Remote or a suitable location)
- Job Description Summary
- Key Responsibilities (5-7 points)
- Required Skills and Technologies
- Experience Level Required
- Education Requirements
- Nice-to-have Skills

Make it realistic and tailored to the candidate's profile."""


async def generate_jd_from_cv(cv_data: Dict[str, Any]) -> str:
    """
    Generate a suitable job description based on the candidate's CV.
    
    Args:
        cv_data: Parsed CV data containing candidate information
        
    Returns:
        Generated job description text
    """
    try:
        logger.info("Generating job description from CV")
        
        gemini = get_gemini_client()
        
        # Extract key information from CV
        name = cv_data.get("name", "Unknown")
        raw_text = cv_data.get("raw_text", "")
        
        # If CV has parsed_data, use that
        if "parsed_data" in cv_data:
            parsed = cv_data["parsed_data"]
            summary = parsed.get("summary", "")
            work_exp = parsed.get("work_experience", [])
            skills = parsed.get("skills", [])
            education = parsed.get("education", [])
        else:
            summary = cv_data.get("summary", "")
            work_exp = cv_data.get("work_experience", [])
            skills = cv_data.get("skills", [])
            education = cv_data.get("education", [])
        
        # Construct a concise CV summary for JD generation
        cv_summary = f"""
Candidate Name: {name}

Professional Summary:
{summary if summary else "See work experience below"}

Work Experience:
"""
        
        # Add work experience
        if work_exp and len(work_exp) > 0:
            for i, exp in enumerate(work_exp[:3], 1):  # Only include first 3 positions
                if isinstance(exp, dict):
                    title = exp.get("title", "")
                    company = exp.get("company", "")
                    cv_summary += f"\n{i}. {title} at {company}"
                    if "achievements" in exp and exp["achievements"]:
                        cv_summary += f"\n   Key achievements: {', '.join(exp['achievements'][:2])}"
        
        # Add skills
        if skills and len(skills) > 0:
            cv_summary += f"\n\nKey Skills: {', '.join(skills[:15]) if isinstance(skills, list) else skills}"
        
        # Add education
        if education and len(education) > 0:
            cv_summary += "\n\nEducation:"
            for edu in education[:2]:
                if isinstance(edu, dict):
                    degree = edu.get("degree", "")
                    field = edu.get("field", "")
                    university = edu.get("university", "")
                    cv_summary += f"\n- {degree} in {field} from {university}"
        
        # If summary is too short, use raw text
        if len(cv_summary.strip()) < 200 and raw_text:
            cv_summary = raw_text[:2000]  # Use first 2000 chars of raw text
        
        user_prompt = f"""{JD_GENERATION_PROMPT}

Here is the candidate's CV information:

{cv_summary}

Based on this CV, generate a comprehensive and realistic job description that would be a good match for this candidate. The job should be challenging but achievable, representing a logical next step in their career.

Format the output as a complete job description ready to be posted."""

        # Generate JD using Gemini
        jd_text = await gemini.chat(
            system_prompt="You are an expert recruiter and job description writer.",
            user_prompt=user_prompt,
            temperature=0.7
        )
        
        if not jd_text or len(jd_text.strip()) < 100:
            raise ValueError("Generated job description is too short or empty")
        
        logger.info(f"Successfully generated JD ({len(jd_text)} characters)")
        return jd_text.strip()
        
    except Exception as e:
        logger.error(f"Error generating JD from CV: {str(e)}")
        # Return a generic JD as fallback
        return generate_fallback_jd()


def generate_fallback_jd() -> str:
    """Generate a generic fallback job description."""
    return """Software Engineer - Full Stack Development

We are seeking a talented Software Engineer to join our growing team. This role involves working on cutting-edge web applications and contributing to the full software development lifecycle.

Key Responsibilities:
- Design, develop, and maintain web applications
- Write clean, maintainable, and efficient code
- Collaborate with cross-functional teams
- Participate in code reviews and technical discussions
- Troubleshoot and debug applications
- Contribute to architecture and design decisions

Required Skills:
- Strong programming skills in modern languages (Python, JavaScript, Java, etc.)
- Experience with web frameworks and technologies
- Understanding of databases and data modeling
- Knowledge of software development best practices
- Problem-solving and analytical skills
- Good communication and teamwork abilities

Experience: 2-5 years in software development

Education: Bachelor's degree in Computer Science or related field (or equivalent experience)

Nice to Have:
- Cloud platform experience (AWS, Azure, GCP)
- DevOps and CI/CD knowledge
- Agile/Scrum experience
- Open source contributions
"""
