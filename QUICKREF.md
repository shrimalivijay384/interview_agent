# Interview Agent - Quick Reference

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GEMINI_API_KEY

# Frontend
cd frontend
npm install
```

### 2. Run Application
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
backend/app/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration & env vars
├── models/              # Pydantic data models
├── services/            # Business logic
│   ├── gemini_client.py      # Gemini API wrapper
│   ├── resume_parser.py      # Resume parsing
│   ├── jd_parser.py          # JD parsing
│   ├── kpi_decider.py        # KPI generation
│   ├── question_agent.py     # Interview logic
│   └── research.py           # External APIs
└── routes/              # API endpoints

frontend/src/
├── api/client.ts        # Backend API wrapper
├── context/             # React state management
├── pages/               # Main pages (Home, Interview, Report)
├── styles/              # CSS files
└── types/api.ts         # TypeScript types
```

## 🔑 API Keys

### Google Gemini (Required)
1. Visit: https://makersuite.google.com/app/apikey
2. Create API key
3. Add to `backend/.env`: `GEMINI_API_KEY=your_key`

### Serper (Optional - for web search)
1. Visit: https://serper.dev/
2. Sign up and get API key
3. Add to `backend/.env`: `SERPER_API_KEY=your_key`

## 🧪 Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

## 🔧 Common Commands

### Backend
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run on different port
uvicorn app.main:app --port 8080

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## 📝 Sample Data

### Sample Job Description
```
Senior Software Engineer

We're looking for an experienced engineer to join our team.

Requirements:
- 5+ years Python experience
- Strong background in backend development
- Experience with FastAPI, Docker, AWS
- System design skills
- Excellent communication

Responsibilities:
- Design and build scalable APIs
- Lead technical discussions
- Mentor junior developers
```

### Sample Resume
```
John Doe
john@email.com | github.com/johndoe

Senior Software Engineer with 6 years experience

Skills: Python, JavaScript, React, FastAPI, AWS, Docker

Experience:
- Senior Engineer at TechCorp (2020-Present)
  Built microservices, led team of 3 developers
- Engineer at StartupXYZ (2018-2020)
  Developed REST APIs, CI/CD pipelines

Education: BS Computer Science, MIT (2018)
```

## 🐛 Troubleshooting

### Backend Issues
- **Import errors**: Activate venv, reinstall requirements
- **API key error**: Check .env file, verify key is valid
- **Port in use**: Change port in uvicorn command

### Frontend Issues
- **Can't reach backend**: Check backend is running on port 8000
- **Build errors**: Delete node_modules, run `npm install` again
- **CORS errors**: Check CORS settings in backend/app/main.py

## 📊 Flow Diagram

```
User Input (JD + Resume)
    ↓
Parse JD & Resume (Gemini)
    ↓
Determine KPIs (Gemini)
    ↓
Initialize Session
    ↓
Generate Question (Gemini)
    ↓
User Answers
    ↓
Evaluate Answer (Gemini)
    ↓
Update Scores
    ↓
[More Questions?]
    Yes → Generate Next Question
    No  → Generate Final Report
    ↓
Display Results
```

## 🎯 Key Features

1. **AI-Powered Parsing**: Extracts structured data from unstructured text
2. **Intelligent KPIs**: Tailored evaluation criteria based on role and candidate
3. **Adaptive Questions**: Context-aware question generation
4. **Real-time Evaluation**: Instant feedback on answers
5. **Comprehensive Reports**: Detailed scoring with actionable insights

## 🔗 Useful Links

- Google Gemini API: https://ai.google.dev/
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- Vite Docs: https://vitejs.dev/
