# 🎯 AI Interview Agent

An end-to-end intelligent interview system powered by **Google Gemini AI**, built with **FastAPI** (backend) and **React + TypeScript** (frontend).

## 📋 Overview

This system automates the technical interview process by:

1. **Parsing** job descriptions and candidate resumes using AI
2. **Determining** Key Performance Indicators (KPIs) to evaluate
3. **Conducting** adaptive interviews with tailored questions
4. **Evaluating** responses in real-time with detailed scoring
5. **Generating** comprehensive feedback reports

## 🏗️ Architecture

```
interview_agent/
├── backend/          # FastAPI + Python backend
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Configuration management
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # Business logic
│   │   │   ├── gemini_client.py      # Google Gemini integration
│   │   │   ├── resume_parser.py      # Resume parsing
│   │   │   ├── jd_parser.py          # Job description parsing
│   │   │   ├── kpi_decider.py        # KPI determination
│   │   │   ├── question_agent.py     # Interview orchestration
│   │   │   └── research.py           # External research (Serper)
│   │   └── routes/          # API endpoints
│   └── tests/               # Unit tests
│
└── frontend/         # React + TypeScript frontend
    ├── src/
    │   ├── api/             # API client
    │   ├── context/         # React context
    │   ├── pages/           # Page components
    │   ├── styles/          # CSS styles
    │   └── types/           # TypeScript types
    └── public/
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Serper API Key** (optional, for web search - [Get one here](https://serper.dev/))

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SERPER_API_KEY=your_serper_api_key_here  # Optional
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

5. **Run the backend:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at: `http://localhost:8000`
   
   API docs at: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:5173`

## 📖 Usage

### Starting an Interview

1. Open `http://localhost:5173` in your browser
2. Paste a **Job Description** in the first text area
3. Paste a **Resume/CV** in the second text area
4. Click **"Start Interview"**

The system will:
- Parse both documents using AI
- Determine 5-8 KPIs to evaluate
- Generate the first interview question

### During the Interview

- Read each question carefully
- Type your answer in the text area
- Click **"Submit Answer"**
- The AI evaluates your response and generates the next question
- Track your progress via the KPI overview panel

### Viewing Results

After completing all questions:
- View your **overall score** (0-5 scale)
- See **per-KPI breakdowns** with justifications
- Read **strengths** and **areas for improvement**
- Get a **hiring recommendation**

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```

### Start Interview
```bash
POST /api/interview/start
Content-Type: application/json

{
  "jd_text": "Job description text...",
  "cv_text": "Resume text..."
}

Response:
{
  "session_id": "uuid",
  "first_question": {...},
  "kpis": [...],
  "message": "Welcome message"
}
```

### Submit Answer
```bash
POST /api/interview/answer
Content-Type: application/json

{
  "session_id": "uuid",
  "answer_text": "My answer...",
  "duration_seconds": 45.5
}

Response:
{
  "session_id": "uuid",
  "next_question": {...} or null,
  "evaluation_summary": "Feedback...",
  "is_complete": false,
  "progress": {...}
}
```

### End Interview
```bash
POST /api/interview/end
Content-Type: application/json

{
  "session_id": "uuid"
}

Response:
{
  "session_id": "uuid",
  "report": {
    "overall_score": 3.8,
    "per_kpi_scores": [...],
    "strengths": [...],
    "weaknesses": [...],
    "recommendation": "...",
    "total_questions": 8
  }
}
```

### Get Session Info
```bash
GET /api/interview/session/{session_id}
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_gemini_client.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## 🛠️ Configuration

### Backend Configuration (`backend/app/config.py`)

Key settings:
- `GEMINI_API_KEY`: Google Gemini API key (required)
- `SERPER_API_KEY`: Serper web search key (optional)
- `GEMINI_MODEL`: Model name (default: "gemini-pro")
- `GEMINI_TEMPERATURE`: Response randomness (default: 0.7)
- `MAX_QUESTIONS_PER_INTERVIEW`: Maximum questions (default: 15)
- `MIN_QUESTIONS_PER_INTERVIEW`: Minimum questions (default: 5)

### Frontend Configuration (`frontend/vite.config.ts`)

Proxy settings for API calls:
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 🌟 Features

### Resume & JD Parsing
- **AI-powered extraction** of structured data
- Supports various resume formats
- Extracts: skills, experience, education, projects, certifications
- Parses job requirements, responsibilities, and qualifications

### KPI Decision
- **Intelligent KPI generation** based on job requirements and candidate background
- Weighted scoring (weights sum to 1.0)
- Categorized by type: technical, behavioral, problem-solving, cultural
- Expected proficiency levels: junior, mid, senior, expert

### Interview Orchestration
- **Adaptive questioning** based on previous answers
- Multiple question types: technical, behavioral, system design, situational
- Dynamic difficulty adjustment
- Real-time answer evaluation with Gemini
- Comprehensive session state management

### Research Integration
- **Web search** via Serper API
- GitHub profile lookup (public API)
- LinkedIn search (stub for future implementation)
- Extensible for additional data sources

## 🚧 Future Enhancements

- [ ] **Persistent storage** (PostgreSQL/MongoDB)
- [ ] **User authentication** and session management
- [ ] **Video/audio interviews** support
- [ ] **LinkedIn API integration** for profile verification
- [ ] **Resume file upload** (PDF, DOCX parsing)
- [ ] **Multi-language support**
- [ ] **Interview analytics dashboard**
- [ ] **Custom question templates**
- [ ] **Interview scheduling**
- [ ] **Email notifications**

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version: `python --version` (need 3.11+)
- Verify API key is set in `.env`
- Check port 8000 is not in use

**Frontend can't connect to backend:**
- Ensure backend is running on port 8000
- Check proxy configuration in `vite.config.ts`
- Verify CORS settings in `backend/app/main.py`

**Gemini API errors:**
- Verify API key is valid
- Check quota limits
- Review error logs in backend console

## 📧 Support

For issues or questions, check:
- [API documentation](http://localhost:8000/docs) when backend is running
- Backend logs for detailed error messages
- GitHub issues

---

**Built with ❤️ using Google Gemini, FastAPI, and React**