# 🚀 Interview Agent - Running Successfully!

## ✅ Status

Both backend and frontend servers are now running:

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Status**: ✅ Running (PID: check with `ps aux | grep uvicorn`)

### Frontend (React + Vite)
- **URL**: http://localhost:5173
- **Status**: ✅ Running

### Database
- **Type**: SQLite
- **Location**: `backend/interview_agent.db`
- **Status**: ✅ Initialized with mock data
- **Mock Data**:
  - Job Description: Senior Full Stack Developer at TechCorp Inc. (ID: 1)
  - Resume: John Anderson (ID: 1)

---

## 🎯 How to Use

1. **Open the application**: Navigate to http://localhost:5173 in your browser

2. **Start an interview**:
   - Upload or paste a Job Description
   - Upload or paste a Resume/CV
   - Click "Start Interview"

3. **Answer questions**:
   - The AI will ask relevant questions based on the JD and resume
   - Type your answers and submit
   - Continue until the interview is complete

4. **View report**:
   - See your overall score
   - Review KPI evaluations
   - Read strengths and weaknesses
   - Get hiring recommendation

---

## 🛠️ Managing the Servers

### Stop Backend
```bash
ps aux | grep uvicorn
kill <PID>
```

### Stop Frontend
- Press `Ctrl+C` in the terminal running `npm run dev`
- Or: `ps aux | grep vite` and `kill <PID>`

### Restart Backend
```bash
cd /home/labuser/interview_agent/interview_agent/backend
nohup /home/labuser/interview_agent/interview_agent/.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

### Restart Frontend
```bash
cd /home/labuser/interview_agent/interview_agent/frontend
npm run dev
```

### View Backend Logs
```bash
cd /home/labuser/interview_agent/interview_agent/backend
tail -f backend.log
```

---

## 📝 Configuration

### Environment Variables (.env)
Located at: `backend/.env`

Required:
- `GEMINI_API_KEY`: Your Google Gemini API key (currently placeholder)
- `SERPER_API_KEY`: Optional - for web research features

To use real API:
1. Get a Gemini API key from https://makersuite.google.com/app/apikey
2. Update `backend/.env` with your actual key
3. Restart the backend server

---

## 🧪 Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# API documentation (open in browser)
http://localhost:8000/docs
```

### Using the Frontend
Just open http://localhost:5173 and interact with the UI!

---

## �� Database

### View Database
```bash
cd /home/labuser/interview_agent/interview_agent/backend
sqlite3 interview_agent.db

# Inside sqlite3:
.tables
SELECT * FROM job_descriptions;
SELECT * FROM resumes;
.exit
```

### Reset Database
```bash
cd /home/labuser/interview_agent/interview_agent/backend
rm interview_agent.db
/home/labuser/interview_agent/interview_agent/.venv/bin/python init_db.py
```

---

## ⚠️ Important Notes

1. **API Key**: The current setup uses a placeholder API key. To use real AI features, you need to:
   - Get a Google Gemini API key
   - Update it in `backend/.env`
   - Restart the backend

2. **CORS**: The backend is configured to accept requests from:
   - http://localhost:5173 (default Vite port)
   - http://localhost:3000 (alternative port)

3. **Mock Data**: The database is pre-loaded with:
   - One job description (Senior Full Stack Developer)
   - One resume (John Anderson)

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify Python environment: `/home/labuser/interview_agent/interview_agent/.venv/bin/python --version`
- Check logs: `cat backend/backend.log`

### Frontend won't start
- Check if port 5173 is already in use: `lsof -i :5173`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### Database errors
- Reinitialize: `rm backend/interview_agent.db && python backend/init_db.py`

### API connection errors
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/app/config.py`

---

## 📞 Quick Commands

```bash
# Check if servers are running
curl http://localhost:8000/health
curl http://localhost:5173

# View processes
ps aux | grep -E "uvicorn|vite"

# Stop all
pkill -f uvicorn
pkill -f vite

# View logs
tail -f backend/backend.log
```

---

**Ready to conduct AI-powered interviews! 🎉**
