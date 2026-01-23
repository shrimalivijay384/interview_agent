"""
Unit tests for question agent.
"""
import pytest
from app.models import (
    JobDescription, Resume, KPI, ExperienceLevel,
    InterviewStatus
)
from app.services.question_agent import (
    start_interview, get_next_question, finalize_interview,
    get_session_store
)


class TestQuestionAgent:
    """Test suite for question agent."""
    
    @pytest.fixture
    def sample_jd(self):
        """Sample JD."""
        return JobDescription(
            title="Software Engineer",
            description="Build applications",
            responsibilities=["Code", "Test"],
            required_skills=[]
        )
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume."""
        return Resume(
            name="Test Candidate",
            skills=["Python", "React"],
            work_experience=[],
            education=[]
        )
    
    @pytest.fixture
    def sample_kpis(self):
        """Sample KPIs."""
        return [
            KPI(
                id="kpi_1",
                name="Technical Skills",
                weight=0.5,
                description="Core technical abilities",
                expected_level=ExperienceLevel.MID,
                category="technical"
            ),
            KPI(
                id="kpi_2",
                name="Communication",
                weight=0.5,
                description="Communication skills",
                expected_level=ExperienceLevel.MID,
                category="behavioral"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_start_interview(self, sample_jd, sample_resume, sample_kpis):
        """Test interview initialization."""
        session = await start_interview(sample_jd, sample_resume, sample_kpis)
        
        assert session.id is not None
        assert session.status == InterviewStatus.IN_PROGRESS
        assert len(session.question_history) > 0
        assert session.get_current_question() is not None
    
    @pytest.mark.asyncio
    async def test_get_next_question(self, sample_jd, sample_resume, sample_kpis):
        """Test question generation and answer evaluation."""
        session = await start_interview(sample_jd, sample_resume, sample_kpis)
        
        # Answer first question
        next_q, is_complete, evals = await get_next_question(
            session.id,
            "This is my answer to the first question. I have experience with Python and have built several projects.",
            duration_seconds=30.0
        )
        
        assert len(evals) > 0
        if not is_complete:
            assert next_q is not None
    
    @pytest.mark.asyncio
    async def test_finalize_interview(self, sample_jd, sample_resume, sample_kpis):
        """Test interview finalization."""
        session = await start_interview(sample_jd, sample_resume, sample_kpis)
        
        # Answer a question
        await get_next_question(
            session.id,
            "Sample answer",
            duration_seconds=20.0
        )
        
        # Finalize
        report = await finalize_interview(session.id)
        
        assert report.session_id == session.id
        assert 0 <= report.overall_score <= 5
        assert len(report.per_kpi_scores) > 0
    
    def test_session_store(self, sample_jd, sample_resume, sample_kpis):
        """Test session storage."""
        from app.models import InterviewSession
        
        store = get_session_store()
        session = InterviewSession(
            id="test-123",
            jd=sample_jd,
            resume=sample_resume,
            kpis=sample_kpis
        )
        
        store.create_session(session)
        retrieved = store.get_session("test-123")
        
        assert retrieved is not None
        assert retrieved.id == "test-123"


# TODO: Add more tests
# - Test question difficulty progression
# - Test KPI coverage logic
# - Test edge cases (very short/long answers)
# - Mock Gemini for deterministic testing
