"""
Unit tests for JD parser.
"""
import pytest
from app.services.jd_parser import parse_jd, extract_jd_highlights


SAMPLE_JD = """
Senior Software Engineer

Company: TechCorp Inc.
Location: San Francisco, CA
Type: Full-time

We are looking for an experienced Senior Software Engineer to join our team.

Responsibilities:
- Design and implement scalable backend systems
- Lead technical discussions and architecture decisions
- Mentor junior team members
- Collaborate with cross-functional teams

Required Skills:
- 5+ years of experience in software development
- Strong proficiency in Python and JavaScript
- Experience with cloud platforms (AWS/GCP/Azure)
- Knowledge of microservices architecture
- Excellent communication skills

Preferred Skills:
- Experience with Kubernetes and Docker
- Familiarity with machine learning concepts
- Open source contributions

Education:
Bachelor's degree in Computer Science or related field

Benefits:
- Competitive salary
- Health insurance
- 401(k) matching
- Flexible work hours
- Remote work options
"""


class TestJDParser:
    """Test suite for job description parser."""
    
    @pytest.mark.asyncio
    async def test_parse_jd_basic(self):
        """Test basic JD parsing."""
        jd = await parse_jd(SAMPLE_JD)
        
        assert jd.title is not None
        assert len(jd.responsibilities) > 0
        assert len(jd.required_skills) > 0
        # Note: Exact results depend on Gemini
    
    @pytest.mark.asyncio
    async def test_extract_jd_highlights(self):
        """Test JD highlights extraction."""
        jd = await parse_jd(SAMPLE_JD)
        highlights = await extract_jd_highlights(jd)
        
        assert "title" in highlights
        assert "total_required_skills" in highlights


# TODO: Add more tests
# - Test different JD formats
# - Test skill level classification
# - Test missing fields handling
# - Mock Gemini responses
