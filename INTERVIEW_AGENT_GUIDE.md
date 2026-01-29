# Interview Agent System - Complete Documentation

## Overview

A comprehensive AI-powered interview system using FastAPI, Google Gemini, and Serper API. The system orchestrates 4 specialized agents to conduct end-to-end technical interviews.

## Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                  INTERVIEW ORCHESTRATOR                      │
│              (Unified Coordination Layer)                    │
└─────────────────────────────────────────────────────────────┘
         │         │          │            │
         ▼         ▼          ▼            ▼
    ┌────────┐ ┌──────┐ ┌─────────┐ ┌──────────┐
    │GREETING│ │PROFILE│ │ PROJECT │ │    KPI   │
    │  INFO  │ │VALIDATOR│ │ANALYZER │ │EXTRACTOR │
    │COLLECTOR│ │        │ │         │ │          │
    └────────┘ └────────┘ └─────────┘ └──────────┘
         │         │          │            │
         └─────────┴──────────┴────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  INTERVIEW   │
              │    AGENT     │
              │ (Technical)  │
              └──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │FINAL REPORT  │
              └──────────────┘
```

## Agents

### 1. Greeting & Info Collector Agent
**Purpose**: Welcome candidates and collect basic information

**Stages**:
- **Intro**: Welcome message and interview overview
- **Basic Info**: Collect name, email, phone, experience
- **Cross-check**: Validate against resume data
- **Context**: Gather work history context
- **Enrichment**: Enrich profile with additional details

**API Endpoints**:
```
POST /api/info-collector/start-greeting
POST /api/info-collector/collect-basic-info
POST /api/info-collector/cross-check
POST /api/info-collector/gather-context
POST /api/info-collector/enrich-profile
```

### 2. Profile Validator Agent
**Purpose**: Verify LinkedIn and GitHub profiles

**Stages**:
- **LinkedIn**: Validate LinkedIn profile URL
- **Verify**: Cross-check LinkedIn data
- **GitHub**: Validate GitHub username
- **Verify**: Analyze GitHub repositories
- **Validation**: Generate comprehensive validation report

**API Endpoints**:
```
POST /api/profile-validator/validate-linkedin
POST /api/profile-validator/validate-github
POST /api/profile-validator/cross-validate
GET  /api/profile-validator/{session_id}/report
```

### 3. Project Analyzer Agent
**Purpose**: Deep technical analysis of resume projects

**Stages**:
- **Resume**: Extract projects from resume
- **Projects**: List and categorize projects
- **Technical**: Analyze technical stack and complexity
- **Deep Dive**: Generate technical questions
- **Ask Qs**: Interactive Q&A about projects

**API Endpoints**:
```
POST /api/project-analyzer/start-analysis
POST /api/project-analyzer/analyze-project
POST /api/project-analyzer/submit-answer
GET  /api/project-analyzer/{session_id}/report
```

### 4. KPI Extractor Agent
**Purpose**: Extract Key Performance Indicators from Job Description

**Stages**:
- **Parse JD**: Extract structured data from job description
- **Extract KPIs**: Identify 5-8 critical competencies
- **Identify Metrics**: Define measurable criteria for each KPI

**Features**:
- Context-aware KPI extraction
- Weighted KPI system
- Category-based classification (technical, behavioral, problem_solving, cultural, domain)
- Measurable evaluation criteria

**API Endpoints**:
```
POST /api/unified-interview/kpi-extraction/extract
```

### 5. Interview Agent (Main)
**Purpose**: Conduct KPI-based technical interviews

**Features**:
- Generate targeted questions based on KPIs
- Real-time answer evaluation
- Multi-dimensional scoring
- Comprehensive assessment reports

**API Endpoints**:
```
POST /api/unified-interview/interview/start-standalone
POST /api/unified-interview/interview/{session_id}/answer
GET  /api/unified-interview/interview/{session_id}/report-standalone
```

## Unified Interview Flow

### Complete Interview Pipeline

```
START
  ↓
1. GREETING & INFO COLLECTION
   - Welcome candidate
   - Collect basic information
   - Cross-check with resume
  ↓
2. PROFILE VALIDATION
   - Validate LinkedIn profile
   - Validate GitHub profile
   - Generate validation report
  ↓
3. PROJECT ANALYSIS
   - Extract resume projects
   - Analyze technical depth
   - Ask deep-dive questions
  ↓
4. KPI EXTRACTION
   - Parse job description
   - Extract evaluation KPIs
   - Identify metrics
  ↓
5. TECHNICAL INTERVIEW
   - Generate KPI-based questions
   - Conduct Q&A
   - Evaluate answers
  ↓
6. FINAL REPORT
   - Compile all data
   - Generate comprehensive report
   - Provide hire recommendation
  ↓
COMPLETE
```

### Unified API Endpoints

#### Start Interview
```bash
POST /api/unified-interview/start
{
  "jd_text": "Job description...",
  "resume_id": 1
}
```

#### Process Action
```bash
POST /api/unified-interview/{session_id}/action
{
  "action": "submit_greeting_response",
  "data": {
    "response": "Hello, I'm ready to begin!"
  }
}
```

**Available Actions by Stage**:
- **Greeting**: `submit_greeting_response`
- **Info Collection**: `submit_basic_info`
- **Profile Validation**: `submit_linkedin_url`, `submit_github_url`
- **Project Analysis**: `start_project_analysis`, `submit_project_answer`
- **KPI Extraction**: `extract_kpis`
- **Technical Interview**: `submit_interview_answer`
- **Final Report**: `generate_final_report`

#### Get Status
```bash
GET /api/unified-interview/{session_id}/status
```

#### Get Final Report
```bash
GET /api/unified-interview/{session_id}/report
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite

### Backend Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment**:
The `.env` file is already configured with:
```
GEMINI_API_KEY=AIzaSyDeF0GTiaE0dULNMMmMj9NVYEZ7gTGoo5I
SERPER_API_KEY=3ad4c25460c9d6f33235c5f9750cc666e503f6ca
ENVIRONMENT=development
LOG_LEVEL=INFO
```

3. **Initialize database**:
```bash
python init_db.py
```

4. **Start backend**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start frontend**:
```bash
npm run dev
```

## API Documentation

Once the backend is running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

### API Keys

- **Gemini API**: `AIzaSyDeF0GTiaE0dULNMMmMj9NVYEZ7gTGoo5I`
- **Serper API**: `3ad4c25460c9d6f33235c5f9750cc666e503f6ca`

### Database

- **Type**: SQLite
- **Location**: `./interview_agent.db`
- **Models**: JobDescription, Resume, Interview, QAHistory, FinalReport

## Usage Examples

### Example 1: Complete Unified Interview

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Start interview
response = requests.post(f"{BASE_URL}/api/unified-interview/start", json={
    "jd_text": "Senior Full Stack Developer...",
    "resume_id": 1
})
session_id = response.json()["session_id"]

# 2. Submit greeting
requests.post(f"{BASE_URL}/api/unified-interview/{session_id}/action", json={
    "action": "submit_greeting_response",
    "data": {"response": "Hello!"}
})

# 3. Submit basic info
requests.post(f"{BASE_URL}/api/unified-interview/{session_id}/action", json={
    "action": "submit_basic_info",
    "data": {
        "basic_info": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "years_of_experience": 5
        }
    }
})

# 4. Submit LinkedIn
requests.post(f"{BASE_URL}/api/unified-interview/{session_id}/action", json={
    "action": "submit_linkedin_url",
    "data": {"linkedin_url": "https://linkedin.com/in/johndoe"}
})

# 5. Submit GitHub
requests.post(f"{BASE_URL}/api/unified-interview/{session_id}/action", json={
    "action": "submit_github_url",
    "data": {"github_username": "johndoe"}
})

# ... continue through all stages

# Final: Get report
report = requests.get(f"{BASE_URL}/api/unified-interview/{session_id}/report")
print(report.json())
```

### Example 2: Standalone KPI Extraction

```python
response = requests.post(f"{BASE_URL}/api/unified-interview/kpi-extraction/extract", json={
    "jd_text": "We are looking for a Senior Full Stack Developer...",
    "resume_context": {
        "years_of_experience": 7,
        "skills": ["React", "Node.js", "Python"]
    }
})

kpis = response.json()["kpis"]
print(f"Extracted {len(kpis)} KPIs")
```

### Example 3: Standalone Technical Interview

```python
# Start interview
response = requests.post(f"{BASE_URL}/api/unified-interview/interview/start-standalone", json={
    "candidate_name": "John Doe",
    "job_title": "Senior Full Stack Developer",
    "kpis": [
        {
            "id": "kpi_1",
            "name": "React Expertise",
            "weight": 0.25,
            "description": "Advanced React development",
            "expected_level": "senior",
            "category": "technical"
        }
    ],
    "num_questions": 10
})

session_id = response.json()["session_id"]
question = response.json()["current_question"]

# Submit answer
requests.post(f"{BASE_URL}/api/unified-interview/interview/{session_id}/answer", json={
    "question_id": question["id"],
    "answer_text": "React is a JavaScript library..."
})

# Get report
report = requests.get(f"{BASE_URL}/api/unified-interview/interview/{session_id}/report-standalone")
```

## Data Models

### KPI (Key Performance Indicator)
```python
{
    "id": "kpi_1",
    "name": "React Development",
    "weight": 0.20,
    "description": "Proficiency in React",
    "expected_level": "senior",  # junior|mid|senior|expert
    "category": "technical"       # technical|behavioral|problem_solving|cultural|domain
}
```

### Question
```python
{
    "id": "q_1",
    "text": "Explain React hooks and their use cases",
    "kpi_ids": ["kpi_1", "kpi_2"],
    "difficulty": "medium",  # easy|medium|hard
    "question_type": "technical"  # technical|behavioral|system_design|culture|situational
}
```

### KPI Evaluation
```python
{
    "kpi_id": "kpi_1",
    "score": 4.5,  # 0.0 to 5.0
    "justification": "Strong understanding demonstrated...",
    "timestamp": "2026-01-27T10:30:00"
}
```

## Features

### ✅ Implemented Features

1. **Multi-Agent Orchestration**
   - 4 specialized agents working in coordination
   - State management across agents
   - Progress tracking

2. **Intelligent KPI Extraction**
   - AI-powered JD parsing
   - Context-aware KPI identification
   - Measurable metrics definition

3. **Technical Interview**
   - KPI-based question generation
   - Real-time answer evaluation
   - Multi-dimensional scoring

4. **Profile Validation**
   - LinkedIn verification
   - GitHub analysis
   - Cross-validation

5. **Project Analysis**
   - Resume project extraction
   - Technical depth assessment
   - Interactive Q&A

6. **Comprehensive Reporting**
   - Stage-wise reports
   - Final consolidated report
   - Hire recommendations

### 🔄 Integration Points

- **Google Gemini**: AI model for generation and evaluation
- **Serper API**: Web search for profile validation
- **SQLite**: Data persistence
- **FastAPI**: RESTful API framework

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.10+)

2. **Database Errors**
   - Reinitialize database: `python init_db.py`
   - Check database file permissions

3. **API Key Issues**
   - Verify `.env` file exists and contains valid keys
   - Check API key permissions and quotas

4. **Agent Initialization**
   - Ensure all agent services are imported correctly
   - Check logs for initialization errors

## Performance Considerations

- **Caching**: Agents use singleton pattern for efficiency
- **Async Operations**: All AI calls are asynchronous
- **Session Management**: In-memory session storage (consider Redis for production)

## Security Notes

- API keys are stored in `.env` file (never commit to git)
- Input validation using Pydantic models
- CORS configured for local development

## Future Enhancements

- [ ] Redis-based session storage
- [ ] WebSocket support for real-time updates
- [ ] Multi-language support
- [ ] Video interview integration
- [ ] Advanced analytics dashboard
- [ ] LangChain integration
- [ ] Custom agent configuration

## License

Proprietary - Internal Use Only

## Support

For issues or questions, check the logs in:
- Backend: Console output with timestamp
- Database: `interview_agent.db`
- API Docs: http://localhost:8000/docs
