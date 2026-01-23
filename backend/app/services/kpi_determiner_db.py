"""
KPI Determiner service - Determines KPIs based on JD and CV from database using Gemini API.
"""
import logging
import json
from typing import Optional, Dict, List, Any
from ...database import get_jd_by_id, get_candidate_by_id
from .gemini_client import GeminiClient
from ..models import KPI, ExperienceLevel

logger = logging.getLogger(__name__)


class KPIDeterminer:
    """Service for determining KPIs based on job description and candidate CV."""
    
    SYSTEM_PROMPT = """You are an expert technical recruiter and hiring manager with 15+ years of experience. Your task is to analyze a job description and candidate's resume/CV to determine the Key Performance Indicators (KPIs) that should be evaluated during the technical interview.

Your analysis should:
1. Identify 5-8 critical competencies/KPIs based on the job requirements and candidate background
2. Assign appropriate weights (0.0 to 1.0) that sum to 1.0
3. Determine expected proficiency level for each KPI based on the role requirements
4. Categorize each KPI appropriately
5. Provide clear, measurable descriptions

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
1. Prioritize must-have technical requirements from the JD
2. Tailor expectations to the candidate's experience level
3. Balance technical (60-70%) and soft skills (30-40%)
4. Include at least one behavioral/communication KPI
5. Make KPIs specific and measurable
6. Weight must-haves more heavily than nice-to-haves"""

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize the KPI Determiner.
        
        Args:
            gemini_client: Optional Gemini client instance. Creates new one if not provided.
        """
        self.gemini_client = gemini_client or GeminiClient()
        logger.info("KPI Determiner initialized")
    
    def _parse_jd_from_db(self, jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse job description data from database."""
        content = jd_data.get("content", {})
        return {
            "title": content.get("job_title", jd_data.get("title", "Unknown")),
            "company": content.get("company", jd_data.get("company", "Unknown")),
            "location": content.get("location", ""),
            "employment_type": content.get("employment_type", ""),
            "summary": content.get("job_summary", ""),
            "responsibilities": content.get("responsibilities", []),
            "required_skills": content.get("required_skills", []),
            "preferred_skills": content.get("preferred_skills", []),
            "experience_required": content.get("experience_required", ""),
            "education_required": content.get("education_required", ""),
            "benefits": content.get("benefits", [])
        }
    
    def _parse_cv_from_db(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse candidate CV data from database."""
        content = cv_data.get("content", {})
        return {
            "name": content.get("name", cv_data.get("name", "Unknown")),
            "email": content.get("email", cv_data.get("email", "")),
            "phone": content.get("phone", ""),
            "summary": content.get("summary", ""),
            "skills": content.get("skills", []),
            "experience": content.get("experience", []),
            "education": content.get("education", []),
            "certifications": content.get("certifications", []),
            "projects": content.get("projects", [])
        }
    
    def _extract_years_of_experience(self, cv: Dict[str, Any]) -> int:
        """Extract approximate years of experience from CV."""
        experience_items = cv.get("experience", [])
        if not experience_items:
            return 0
        
        # Simple estimation based on number of positions
        # Each position ~2 years on average
        return len(experience_items) * 2
    
    def _determine_experience_level(self, years: int) -> str:
        """Determine experience level based on years."""
        if years < 2:
            return "junior"
        elif years < 5:
            return "mid"
        elif years < 8:
            return "senior"
        else:
            return "expert"
    
    async def determine_kpis_from_db(
        self,
        jd_id: int,
        candidate_id: int
    ) -> Dict[str, Any]:
        """
        Determine KPIs based on JD and CV from database.
        
        Args:
            jd_id: ID of job description in database
            candidate_id: ID of candidate CV in database
            
        Returns:
            Dictionary containing:
            - kpis: List of KPI dictionaries
            - reasoning: Explanation of KPI selection
            - candidate_info: Candidate name and experience level
            - jd_info: Job title and company
        """
        try:
            logger.info(f"Determining KPIs for candidate {candidate_id} and JD {jd_id}")
            
            # Retrieve data from database
            jd_db = get_jd_by_id(jd_id)
            cv_db = get_candidate_by_id(candidate_id)
            
            if not jd_db:
                raise ValueError(f"Job description with ID {jd_id} not found")
            if not cv_db:
                raise ValueError(f"Candidate with ID {candidate_id} not found")
            
            # Parse data
            jd = self._parse_jd_from_db(jd_db)
            cv = self._parse_cv_from_db(cv_db)
            
            # Prepare prompt
            user_prompt = self._create_user_prompt(jd, cv)
            
            # Call Gemini API
            response = await self.gemini_client.chat(
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=user_prompt,
                json_mode=True,
                temperature=0.5
            )
            
            # Parse response
            kpi_response = self._parse_kpi_response(response)
            
            # Extract years of experience
            years_exp = self._extract_years_of_experience(cv)
            exp_level = self._determine_experience_level(years_exp)
            
            result = {
                "kpis": kpi_response.get("kpis", []),
                "reasoning": kpi_response.get("reasoning", ""),
                "candidate_info": {
                    "name": cv.get("name"),
                    "email": cv.get("email"),
                    "years_of_experience": years_exp,
                    "experience_level": exp_level
                },
                "jd_info": {
                    "title": jd.get("title"),
                    "company": jd.get("company")
                },
                "database_ids": {
                    "jd_id": jd_id,
                    "candidate_id": candidate_id
                }
            }
            
            logger.info(f"Successfully determined {len(kpi_response.get('kpis', []))} KPIs")
            return result
            
        except Exception as e:
            logger.error(f"Error determining KPIs: {str(e)}")
            raise
    
    def _create_user_prompt(self, jd: Dict[str, Any], cv: Dict[str, Any]) -> str:
        """Create the user prompt for Gemini API."""
        jd_str = json.dumps(jd, indent=2)
        cv_str = json.dumps(cv, indent=2)
        
        prompt = f"""Please analyze the following job description and candidate's CV to determine the Key Performance Indicators (KPIs) that should be evaluated during the technical interview.

Return your analysis in this exact JSON structure:
{{
  "kpis": [
    {{
      "id": "kpi_1",
      "name": "Short KPI name",
      "weight": 0.20,
      "description": "Detailed description of what this KPI measures and why it's important for this role",
      "expected_level": "junior|mid|senior|expert",
      "category": "technical|behavioral|problem_solving|cultural|domain"
    }}
  ],
  "reasoning": "Paragraph explaining your KPI selection strategy, how it aligns with the role requirements and candidate background"
}}

Important requirements:
- Include exactly 5-8 KPIs
- IDs must follow pattern kpi_1, kpi_2, kpi_3, etc.
- Weights must sum to exactly 1.0
- Mix of technical (60-70%) and soft skills (30-40%)
- Return ONLY valid JSON, no additional text

JOB DESCRIPTION:
{jd_str}

CANDIDATE CV:
{cv_str}"""
        
        return prompt
    
    def _parse_kpi_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate Gemini response."""
        try:
            # Try to extract JSON from response
            # Handle case where response might be wrapped in markdown code blocks
            response_text = response.strip()
            
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Validate structure
            if "kpis" not in data:
                raise ValueError("Response missing 'kpis' field")
            
            # Validate and normalize KPIs
            kpis = data.get("kpis", [])
            for kpi in kpis:
                # Ensure required fields
                required_fields = ["id", "name", "weight", "description", "expected_level", "category"]
                for field in required_fields:
                    if field not in kpi:
                        raise ValueError(f"KPI missing required field: {field}")
                
                # Validate weight
                weight = kpi.get("weight", 0)
                if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                    raise ValueError(f"Invalid weight for KPI {kpi.get('id')}: {weight}")
            
            # Normalize weights to sum to 1.0
            total_weight = sum(kpi.get("weight", 0) for kpi in kpis)
            if total_weight > 0:
                for kpi in kpis:
                    kpi["weight"] = round(kpi.get("weight", 0) / total_weight, 3)
            
            return {
                "kpis": kpis,
                "reasoning": data.get("reasoning", "")
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid JSON in Gemini response: {str(e)}")
    
    def format_kpis_for_display(self, kpi_response: Dict[str, Any]) -> str:
        """Format KPI response for human-readable display."""
        output = f"\n{'='*80}\n"
        output += f"KPI EVALUATION FRAMEWORK\n"
        output += f"{'='*80}\n\n"
        
        candidate_info = kpi_response.get("candidate_info", {})
        jd_info = kpi_response.get("jd_info", {})
        
        output += f"Candidate: {candidate_info.get('name')} ({candidate_info.get('experience_level')})\n"
        output += f"Experience: {candidate_info.get('years_of_experience')} years\n"
        output += f"Position: {jd_info.get('title')} @ {jd_info.get('company')}\n\n"
        
        output += f"{'Reasoning:'}\n{kpi_response.get('reasoning', '')}\n\n"
        
        output += f"{'-'*80}\n"
        output += f"{'KPI':<30} {'Weight':<10} {'Level':<12} {'Category':<15}\n"
        output += f"{'-'*80}\n"
        
        for kpi in kpi_response.get("kpis", []):
            output += f"{kpi.get('name', ''):<30} {kpi.get('weight', 0)*100:>6.1f}% {kpi.get('expected_level', ''):<12} {kpi.get('category', ''):<15}\n"
            output += f"  {kpi.get('description', '')}\n\n"
        
        output += f"{'='*80}\n"
        
        return output


# Singleton instance
_kpi_determiner: Optional[KPIDeterminer] = None


def get_kpi_determiner(gemini_client: Optional[GeminiClient] = None) -> KPIDeterminer:
    """Get or create singleton KPI Determiner instance."""
    global _kpi_determiner
    if _kpi_determiner is None:
        _kpi_determiner = KPIDeterminer(gemini_client)
    return _kpi_determiner
