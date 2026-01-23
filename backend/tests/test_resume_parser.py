"""
Unit tests for resume parser.
"""
import pytest
from app.services.resume_parser import parse_resume, extract_resume_highlights


SAMPLE_RESUME = """
John Doe
john.doe@email.com | (555) 123-4567
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

SUMMARY
Experienced software engineer with 5+ years in full-stack development.

SKILLS
Python, JavaScript, React, FastAPI, AWS, Docker, PostgreSQL

EXPERIENCE
Senior Software Engineer | Tech Corp | 2020 - Present
- Led development of microservices architecture
- Improved system performance by 40%
- Mentored junior developers

Software Engineer | StartupXYZ | 2018 - 2020
- Built RESTful APIs using Python and FastAPI
- Implemented CI/CD pipelines

EDUCATION
BS Computer Science | University of Technology | 2014 - 2018
GPA: 3.8/4.0

PROJECTS
E-commerce Platform
- Built full-stack application using React and Node.js
- Deployed on AWS with Docker

CERTIFICATIONS
AWS Certified Solutions Architect
"""


class TestResumeParser:
    """Test suite for resume parser."""
    
    @pytest.mark.asyncio
    async def test_parse_resume_basic(self):
        """Test basic resume parsing."""
        resume = await parse_resume(SAMPLE_RESUME)
        
        assert resume.name is not None
        assert len(resume.skills) > 0
        # Note: Exact parsing results depend on Gemini
    
    @pytest.mark.asyncio
    async def test_extract_highlights(self):
        """Test resume highlights extraction."""
        resume = await parse_resume(SAMPLE_RESUME)
        highlights = await extract_resume_highlights(resume)
        
        assert "name" in highlights
        assert "unique_technologies" in highlights


# TODO: Add more tests
# - Test parsing different resume formats
# - Test handling of missing fields
# - Test error cases (empty resume, invalid format)
# - Mock Gemini responses for faster testing
