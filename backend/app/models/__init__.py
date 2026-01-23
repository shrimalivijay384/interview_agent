"""
Core data models for the interview system.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level for skills and requirements."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXPERT = "expert"


class QuestionType(str, Enum):
    """Type of interview question."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CULTURE = "culture"
    SITUATIONAL = "situational"


class Difficulty(str, Enum):
    """Question difficulty level."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewStatus(str, Enum):
    """Interview session status."""
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Resume Components
class WorkExperienceItem(BaseModel):
    """Single work experience entry."""
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    """Single education entry."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    """Single project entry."""
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    role: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Resume(BaseModel):
    """Parsed resume/CV data."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


# Job Description Components
class RequiredSkill(BaseModel):
    """Required skill with level."""
    name: str
    level: ExperienceLevel = ExperienceLevel.MID
    is_required: bool = True


class JobDescription(BaseModel):
    """Parsed job description."""
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[RequiredSkill] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)


# KPI and Assessment
class KPI(BaseModel):
    """Key Performance Indicator to evaluate during interview."""
    id: str
    name: str
    weight: float = Field(ge=0.0, le=1.0, description="Weight between 0 and 1")
    description: str
    expected_level: ExperienceLevel = ExperienceLevel.MID
    category: str = "technical"  # technical, behavioral, cultural, etc.


class KPIEval(BaseModel):
    """Evaluation of a KPI after an answer."""
    kpi_id: str
    score: float = Field(ge=0.0, le=5.0, description="Score between 0 and 5")
    justification: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Interview Components
class Question(BaseModel):
    """Interview question."""
    id: str
    text: str
    kpi_ids: List[str] = Field(default_factory=list)
    difficulty: Difficulty = Difficulty.MEDIUM
    question_type: QuestionType = QuestionType.TECHNICAL
    context: Optional[str] = None  # Additional context for the question
    follow_up: bool = False  # Is this a follow-up question?


class Answer(BaseModel):
    """Candidate's answer to a question."""
    question_id: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: Optional[float] = None


class QuestionAnswerPair(BaseModel):
    """A question and its corresponding answer."""
    question: Question
    answer: Optional[Answer] = None
    evaluations: List[KPIEval] = Field(default_factory=list)


class InterviewSession(BaseModel):
    """Complete interview session state."""
    id: str
    jd: JobDescription
    resume: Resume
    kpis: List[KPI]
    status: InterviewStatus = InterviewStatus.INITIALIZED
    question_history: List[QuestionAnswerPair] = Field(default_factory=list)
    kpi_scores: dict[str, List[float]] = Field(default_factory=dict)  # kpi_id -> list of scores
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)  # For any additional data
    
    def get_current_question(self) -> Optional[Question]:
        """Get the current unanswered question."""
        if self.question_history and not self.question_history[-1].answer:
            return self.question_history[-1].question
        return None
    
    def get_average_kpi_score(self, kpi_id: str) -> float:
        """Calculate average score for a KPI."""
        scores = self.kpi_scores.get(kpi_id, [])
        return sum(scores) / len(scores) if scores else 0.0
    
    def add_kpi_score(self, kpi_id: str, score: float):
        """Add a score for a KPI."""
        if kpi_id not in self.kpi_scores:
            self.kpi_scores[kpi_id] = []
        self.kpi_scores[kpi_id].append(score)


class FinalReport(BaseModel):
    """Final interview assessment report."""
    session_id: str
    overall_score: float = Field(ge=0.0, le=5.0)
    per_kpi_scores: List[KPIEval]
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str
    detailed_feedback: Optional[str] = None
    total_questions: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# API Request/Response Models
class StartInterviewRequest(BaseModel):
    """Request to start an interview."""
    jd_text: str
    cv_text: str


class StartInterviewResponse(BaseModel):
    """Response when starting an interview."""
    session_id: str
    first_question: Question
    kpis: List[KPI]
    message: str = "Interview session started successfully"


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    session_id: str
    answer_text: str
    duration_seconds: Optional[float] = None


class SubmitAnswerResponse(BaseModel):
    """Response after submitting an answer."""
    session_id: str
    next_question: Optional[Question] = None
    evaluation_summary: Optional[str] = None
    is_complete: bool = False
    progress: dict = Field(default_factory=dict)  # Progress information


class EndInterviewRequest(BaseModel):
    """Request to end an interview."""
    session_id: str


class EndInterviewResponse(BaseModel):
    """Response when ending an interview."""
    session_id: str
    report: FinalReport


# Research/External Data
class SearchResult(BaseModel):
    """Web search result."""
    title: str
    url: str
    snippet: str
    source: str = "serper"
