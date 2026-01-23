# Web Research Integration - Quick Start

## What's New

You now have **web research capabilities** integrated into your Interview Agent using Serper AI API. This allows you to:

- 🔍 **Search the web** for any information
- 💼 **Find LinkedIn profiles** by name and company
- 🐙 **Get GitHub profiles** with repository and statistics
- 👤 **Research candidates** across multiple platforms
- 🏢 **Research companies** for interview preparation

## API Configuration

Your Serper API key is already configured:
```
SERPER_API_KEY=d5b43a6ce43430805cc5d95c2d5a0ec01e2a9f80
```

## Available Endpoints

### 1. Status Check
```bash
curl http://localhost:8000/api/research/status
```

### 2. Web Search
```bash
curl -X POST http://localhost:8000/api/research/web-search \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query", "num_results": 5}'
```

### 3. GitHub Profile Lookup
```bash
curl -X POST http://localhost:8000/api/research/github \
  -H "Content-Type: application/json" \
  -d '{"username_or_name": "torvalds"}'
```

### 4. LinkedIn Profile Lookup
```bash
curl -X POST http://localhost:8000/api/research/linkedin \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith", "company": "Google"}'
```

### 5. Candidate Research (All Platforms)
```bash
curl -X POST http://localhost:8000/api/research/candidate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Johnson",
    "email": "sarah@example.com",
    "github": "sjohnson"
  }'
```

### 6. Company Research
```bash
curl -X POST http://localhost:8000/api/research/company \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Google"}'
```

## Features

✅ **Web Search** - General purpose search using Serper API
✅ **LinkedIn Integration** - Find candidates on LinkedIn
✅ **GitHub Integration** - Get GitHub profiles with repositories
✅ **Comprehensive Research** - Single endpoint for all platforms
✅ **Company Research** - Research companies for interview prep
✅ **Error Handling** - Graceful fallbacks if profiles not found

## Implementation Details

- **Service File**: `/backend/app/services/research.py`
- **Routes File**: `/backend/app/routes/research.py`
- **API Key**: Stored in `.env` (not committed to git)
- **Documentation**: See `/backend/WEB_RESEARCH_GUIDE.md`

## Usage Workflow

### Before Interview:
```python
# Research the candidate
research_result = POST /api/research/candidate
# Get LinkedIn, GitHub, and web presence

# Research the company
company_info = POST /api/research/company
# Understand company background
```

### During Interview:
- Use candidate's GitHub profile to discuss projects
- Reference their LinkedIn experience
- Ask about open-source contributions if found

### Post Interview:
- Verify credentials
- Cross-reference with online profiles

## Example Responses

### Web Search Response:
```json
{
  "success": true,
  "data": {
    "query": "machine learning engineer",
    "results": [
      {
        "title": "What Is a Machine Learning Engineer?",
        "url": "https://example.com",
        "snippet": "Machine learning engineers...",
        "source": "serper"
      }
    ]
  }
}
```

### GitHub Response:
```json
{
  "success": true,
  "data": {
    "username": "torvalds",
    "profile_summary": "GitHub Profile: https://github.com/torvalds\nName: Linus Torvalds\nPublic Repos: 11\nFollowers: 279841..."
  }
}
```

### Candidate Research Response:
```json
{
  "success": true,
  "data": {
    "name": "Sarah Johnson",
    "linkedin": "LinkedIn profile found: ...",
    "github": "GitHub profile found: ...",
    "web_presence": [
      {"title": "...", "url": "...", "snippet": "..."}
    ]
  }
}
```

## Limitations & Notes

- **Free Tier**: Serper provides 100 searches/month free
- **Rate Limit**: GitHub API: 60 requests/hour unauthenticated
- **Privacy**: All searches use public data only
- **LinkedIn**: Uses web search (no direct API)
- **Fallback**: If direct lookup fails, uses web search as backup

## Rate Limits

- **Serper**: 100/month (free), unlimited (paid)
- **GitHub**: 60/hour (unauthenticated), 5000/hour (authenticated)

## Future Improvements

1. Cache research results
2. LinkedIn official API (when available)
3. Twitter/X integration
4. Portfolio website analysis
5. Stack Overflow profile lookup

## Next Steps

1. ✅ API key configured
2. ✅ Endpoints tested and working
3. 📝 Read full guide: `WEB_RESEARCH_GUIDE.md`
4. 🔧 Integrate into interview workflow
5. 📊 Add analytics/logging

---

**Status**: ✅ Fully Operational
**Version**: 1.0.0
**Last Updated**: January 23, 2026
