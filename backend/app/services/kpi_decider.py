"""
KPI Decider service - determines evaluation criteria based on JD and Resume.
"""
import logging
import json
from typing import List
from app.models import JobDescription, Resume, KPI, ExperienceLevel
from app.services.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)


KPI_DECIDER_SYSTEM_PROMPT = """You are an expert technical recruiter and hiring manager. Your task is to analyze a job description and candidate's resume to determine the Key Performance Indicators (KPIs) that should be evaluated during the interview.

Your analysis should:
1. Identify 5-8 critical competencies/KPIs based on the job requirements
2. Consider the candidate's background and tailor KPIs accordingly
3. Assign appropriate weights (0.0 to 1.0) - weights should sum to approximately 1.0
4. Determine expected proficiency level for each KPI
5. Categorize KPIs (technical, behavioral, cultural, etc.)
6. Provide clear descriptions of what each KPI measures

KPI Categories:
- technical: Technical skills, coding, architecture, tools
- behavioral: Communication, teamwork, leadership
- problem_solving: Analytical thinking, debugging, system design
- cultural: Company fit, work style, values alignment
- domain: Industry-specific knowledge

Expected Levels:
- junior: Entry-level, 0-2 years equivalent
- mid: Intermediate, 2-5 years equivalent
- senior: Advanced, 5-8 years equivalent
- expert: Expert/Principal, 8+ years equivalent

Guidelines:
- Prioritize must-have requirements from JD
- Consider candidate's experience level
- Balance technical and soft skills
- Include at least one behavioral KPI
- Make KPIs specific and measurable"""


async def decide_kpis(jd: JobDescription, resume: Resume) -> List[KPI]:
    """
    Determine KPIs to evaluate based on job description and candidate resume.
    
    Args:
        jd: Parsed job description
        resume: Parsed candidate resume
        
    Returns:
        List of KPIs to evaluate during interview
    """
    try:
        logger.info("Starting KPI decision process")
        
        gemini = get_gemini_client()
        
        # Prepare JD and Resume summaries
        jd_json = jd.model_dump_json(indent=2)
        resume_json = resume.model_dump_json(indent=2)
        
        user_prompt = f"""Based on the following job description and candidate resume, determine 5-8 Key Performance Indicators (KPIs) to evaluate during the interview.

Return your analysis in this exact JSON structure:

{{
  "kpis": [
    {{
      "id": "kpi_1",
      "name": "Short KPI name",
      "weight": 0.20,
      "description": "Detailed description of what this KPI measures and why it's important",
      "expected_level": "junior|mid|senior|expert",
      "category": "technical|behavioral|problem_solving|cultural|domain"
    }}
  ],
  "reasoning": "Brief explanation of your KPI selection strategy"
}}

Ensure:
- IDs are unique and follow pattern kpi_1, kpi_2, etc.
- Weights sum to approximately 1.0
- Mix of technical and soft skills
- KPIs are specific to this role and candidate

Job Description:
{jd_json}

Candidate Resume:
{resume_json}"""
        
        # Get JSON response from Gemini
        result = await gemini.chat_with_json_response(
            system_prompt=KPI_DECIDER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.5
        )
        
        # Extract and validate KPIs
        kpi_data = result.get("kpis", [])
        reasoning = result.get("reasoning", "")
        
        kpis = [KPI(**kpi) for kpi in kpi_data]
        
        # Normalize weights to sum to 1.0
        total_weight = sum(kpi.weight for kpi in kpis)
        if total_weight > 0:
            for kpi in kpis:
                kpi.weight = kpi.weight / total_weight
        
        logger.info(f"Successfully determined {len(kpis)} KPIs")
        logger.info(f"KPI selection reasoning: {reasoning}")
        
        # Log KPI summary
        for kpi in kpis:
            logger.debug(f"KPI: {kpi.name} (weight: {kpi.weight:.2f}, level: {kpi.expected_level}, category: {kpi.category})")
        
        return kpis
        
    except Exception as e:
        logger.error(f"Error in KPI decision: {str(e)}")
        # Fallback to basic KPIs if Gemini fails
        return _get_fallback_kpis(jd)


def _get_fallback_kpis(jd: JobDescription) -> List[KPI]:
    """
    Generate basic fallback KPIs if Gemini-based decision fails.
    
    Args:
        jd: Job description
        
    Returns:
        List of basic KPIs
    """
    logger.warning("Using fallback KPI generation")
    
    fallback_kpis = [
        KPI(
            id="kpi_technical_1",
            name="Core Technical Skills",
            weight=0.30,
            description=f"Proficiency in key technical skills required for {jd.title}",
            expected_level=ExperienceLevel.MID,
            category="technical"
        ),
        KPI(
            id="kpi_problem_solving",
            name="Problem Solving",
            weight=0.25,
            description="Ability to analyze and solve complex problems",
            expected_level=ExperienceLevel.MID,
            category="problem_solving"
        ),
        KPI(
            id="kpi_communication",
            name="Communication Skills",
            weight=0.15,
            description="Clear communication and explanation of technical concepts",
            expected_level=ExperienceLevel.MID,
            category="behavioral"
        ),
        KPI(
            id="kpi_experience",
            name="Relevant Experience",
            weight=0.20,
            description="Depth and relevance of past work experience",
            expected_level=ExperienceLevel.MID,
            category="technical"
        ),
        KPI(
            id="kpi_cultural_fit",
            name="Cultural Fit",
            weight=0.10,
            description="Alignment with company values and team dynamics",
            expected_level=ExperienceLevel.MID,
            category="cultural"
        )
    ]
    
    return fallback_kpis


async def explain_kpis(kpis: List[KPI]) -> str:
    """
    Generate a human-friendly explanation of the selected KPIs.
    
    Args:
        kpis: List of KPIs
        
    Returns:
        Explanation text
    """
    explanation = "Based on the job requirements and your background, we'll evaluate you on the following criteria:\n\n"
    
    for i, kpi in enumerate(kpis, 1):
        explanation += f"{i}. **{kpi.name}** (Weight: {kpi.weight*100:.0f}%)\n"
        explanation += f"   {kpi.description}\n"
        explanation += f"   Expected level: {kpi.expected_level.value}\n\n"
    
    return explanation
