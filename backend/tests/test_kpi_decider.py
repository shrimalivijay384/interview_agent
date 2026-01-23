"""
Unit tests for KPI decider.
"""
import pytest
from app.models import JobDescription, Resume, RequiredSkill, ExperienceLevel
from app.services.kpi_decider import decide_kpis, explain_kpis, _get_fallback_kpis


class TestKPIDecider:
    """Test suite for KPI decider."""
    
    @pytest.fixture
    def sample_jd(self):
        """Sample job description for testing."""
        return JobDescription(
            title="Senior Software Engineer",
            company="TechCorp",
            description="Build scalable systems",
            responsibilities=["Design APIs", "Lead team"],
            required_skills=[
                RequiredSkill(name="Python", level=ExperienceLevel.SENIOR, is_required=True),
                RequiredSkill(name="AWS", level=ExperienceLevel.MID, is_required=True)
            ]
        )
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume for testing."""
        return Resume(
            name="Jane Smith",
            email="jane@email.com",
            skills=["Python", "JavaScript", "AWS", "Docker"],
            work_experience=[],
            education=[]
        )
    
    @pytest.mark.asyncio
    async def test_decide_kpis(self, sample_jd, sample_resume):
        """Test KPI decision."""
        kpis = await decide_kpis(sample_jd, sample_resume)
        
        assert len(kpis) > 0
        assert all(0 <= kpi.weight <= 1 for kpi in kpis)
        
        # Check weights sum to approximately 1.0
        total_weight = sum(kpi.weight for kpi in kpis)
        assert 0.95 <= total_weight <= 1.05
    
    def test_fallback_kpis(self, sample_jd):
        """Test fallback KPI generation."""
        kpis = _get_fallback_kpis(sample_jd)
        
        assert len(kpis) > 0
        assert all(kpi.id is not None for kpi in kpis)
    
    @pytest.mark.asyncio
    async def test_explain_kpis(self, sample_jd, sample_resume):
        """Test KPI explanation."""
        kpis = await decide_kpis(sample_jd, sample_resume)
        explanation = await explain_kpis(kpis)
        
        assert len(explanation) > 0
        assert "criteria" in explanation.lower() or "evaluate" in explanation.lower()


# TODO: Add more tests
# - Test KPI categorization
# - Test weight normalization
# - Test edge cases (empty JD/resume)
