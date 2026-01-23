# How to Add Your Gemini API Key

## 📋 Three Ways to Add Your API Key

### **Method 1: Create a `.env` File (RECOMMENDED)**

1. **Create the file** in the backend directory:
   ```bash
   cd /home/labuser/interview_agent/interview_agent/backend
   ```

2. **Create `.env` file**:
   ```bash
   cat > .env << 'EOF'
   GEMINI_API_KEY=your-actual-api-key-here
   EOF
   ```

3. **Replace with your actual key**:
   - Get your Gemini API key from: https://ai.google.dev/
   - Open `.env` file and replace `your-actual-api-key-here` with your real key

4. **Verify it worked**:
   ```bash
   cat .env
   ```

---

### **Method 2: Export Environment Variable**

Run this in your terminal before starting the server:

```bash
export GEMINI_API_KEY="your-actual-api-key-here"
```

Then start the server:
```bash
python -m uvicorn app.main:app --reload
```

---

### **Method 3: System Environment Variable**

Add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
echo 'export GEMINI_API_KEY="your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📂 File Reference

### `app/config.py` - Configuration File
**Location**: `/home/labuser/interview_agent/interview_agent/backend/app/config.py`

```python
class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str                    # ← Your API key goes here
    serper_api_key: str = ""               # Optional
    
    # Gemini Configuration (now using 2.5 Flash Lite)
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048
    
    class Config:
        env_file = ".env"                  # ← Reads from .env file
        case_sensitive = False
```

### `.env` File - Environment Variables
**Location**: `/home/labuser/interview_agent/interview_agent/backend/.env`

```env
GEMINI_API_KEY=sk-...your-api-key...
```

### `.env.example` - Template
**Location**: `/home/labuser/interview_agent/interview_agent/backend/.env.example`

A reference file showing all available configuration options.

---

## 🔑 Getting Your Gemini API Key

1. **Visit**: https://ai.google.dev/
2. **Sign in** with your Google account
3. **Create API Key**:
   - Click "Get API Key" or "Create API Key"
   - Copy the key (it starts with `sk-...` or `AIza...`)
4. **Add to `.env` file**

---

## ⚙️ Configuration Options

All these can be set in `.env` file:

```env
# REQUIRED
GEMINI_API_KEY=your-api-key

# OPTIONAL (defaults provided)
GEMINI_MODEL=gemini-2.5-flash-lite          # Current: gemini-2.5-flash-lite
GEMINI_TEMPERATURE=0.5                      # Range: 0.0-1.0 (lower = more deterministic)
GEMINI_MAX_TOKENS=2048                      # Max response length
ENVIRONMENT=development                     # development or production
LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR

# OPTIONAL (for other features)
SERPER_API_KEY=                             # For web search (optional)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## ✅ Verify Your Setup

### Check if .env file exists:
```bash
ls -la backend/.env
```

### Check if API key is loaded:
```bash
cd backend
python -c "from app.config import get_settings; s = get_settings(); print(f'✅ API Key loaded: {s.gemini_api_key[:10]}...')"
```

### Start server and verify:
```bash
python -m uvicorn app.main:app --reload
# Look for: "Gemini client initialized with model: gemini-2.5-flash-lite"
```

---

## 🚀 Quick Setup (5 Minutes)

```bash
# 1. Navigate to backend
cd /home/labuser/interview_agent/interview_agent/backend

# 2. Create .env file with your API key
echo 'GEMINI_API_KEY=your-actual-api-key-here' > .env

# 3. Edit the file to add your real key
nano .env
# or
vim .env
# or
code .env  # if using VS Code

# 4. Verify database
python view_db.py

# 5. Start the server
python -m uvicorn app.main:app --reload

# 6. Test API (in another terminal)
curl -X POST http://localhost:8000/api/kpi/determine \
  -H "Content-Type: application/json" \
  -d '{"jd_id": 1, "candidate_id": 1}'
```

---

## 🔒 Security Best Practices

✅ **DO:**
- Keep API key in `.env` file (not committed to git)
- Use strong, unique keys
- Rotate keys regularly
- Monitor API usage

❌ **DON'T:**
- Commit `.env` file to git
- Share your API key
- Hardcode keys in source code
- Use the same key across environments

---

## 📝 .gitignore Configuration

Make sure `.env` is in your `.gitignore`:

```bash
# Check if .env is already ignored
grep ".env" /home/labuser/interview_agent/interview_agent/.gitignore

# If not, add it
echo ".env" >> /home/labuser/interview_agent/interview_agent/.gitignore
```

---

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution**: 
```bash
# Create .env file
echo 'GEMINI_API_KEY=your-key' > backend/.env

# Or export it
export GEMINI_API_KEY="your-key"
```

### Issue: "Invalid API key"
**Solution**:
- Check your key is correct (copy from ai.google.dev)
- Make sure there are no extra spaces
- Verify the key hasn't been revoked

### Issue: "Model not found"
**Solution**:
- Ensure you have access to gemini-2.5-flash-lite
- Check your Gemini API plan includes this model

### Issue: Rate limit exceeded
**Solution**:
- Check your API usage at ai.google.dev
- Consider upgrading your plan
- Reduce request frequency

---

## 📚 References

- **Gemini API**: https://ai.google.dev/
- **API Documentation**: https://ai.google.dev/docs
- **Python SDK**: https://github.com/google/generative-ai-python
- **Models List**: https://ai.google.dev/models

---

## Summary

| Step | Action | Command |
|------|--------|---------|
| 1 | Navigate to backend | `cd backend` |
| 2 | Get API key | Go to https://ai.google.dev/ |
| 3 | Create .env file | `echo 'GEMINI_API_KEY=...' > .env` |
| 4 | Verify setup | `python view_db.py` |
| 5 | Start server | `python -m uvicorn app.main:app --reload` |
| 6 | Test API | `curl -X POST http://localhost:8000/api/kpi/determine ...` |

**You're all set! Start the server and enjoy the KPI determination feature.** 🚀

---

**Configuration File**: `app/config.py`  
**Environment File**: `.env` (create this)  
**Template File**: `.env.example`  
**Status**: ✅ Ready to add your API key
