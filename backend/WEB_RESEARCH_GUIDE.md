# Web Research Integration Guide

## Overview

The Interview Agent now includes comprehensive web research capabilities using **Serper AI API** for LinkedIn and GitHub research, enabling candidate profiling and background verification.

## Features

### 1. **Web Search**
- General web search using Serper API
- Configurable number of results (1-10)
- Returns title, URL, and snippet for each result

### 2. **LinkedIn Lookup**
- Search for LinkedIn profiles by candidate name
- Optional company filtering for better matching
- Returns LinkedIn profile URL and preview

### 3. **GitHub Lookup**
- Direct GitHub API integration (no authentication required)
- Returns comprehensive profile information:
  - Public repositories count
  - Follower/following statistics
  - Bio and profile details
  - Top 5 recent repositories with star counts
  - Programming languages used

### 4. **Candidate Research**
- Comprehensive research across multiple platforms
- Combines LinkedIn, GitHub, and web presence
- Single endpoint for all candidate information
- Supports optional GitHub username for direct lookup

### 5. **Company Research**
- Research company information
- Searches for: About page, Career page, Company overview
- Returns multiple sources

## API Endpoints

### Web Search
```
POST /api/research/web-search
```

**Request:**
```json
{
  "query": "machine learning engineer",
  "num_results": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "machine learning engineer",
    "results": [
      {
        "title": "Result title",
        "url": "https://example.com",
        "snippet": "Result snippet...",
        "source": "serper"
      }
    ]
  }
}
```

---

### LinkedIn Lookup
```
POST /api/research/linkedin
```

**Request:**
```json
{
  "name": "John Smith",
  "company": "Google"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "John Smith",
    "company": "Google",
    "profile_summary": "LinkedIn profile found: https://linkedin.com/in/...\nPreview: ..."
  }
}
```

---

### GitHub Lookup
```
POST /api/research/github
```

**Request:**
```json
{
  "username_or_name": "torvalds"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "torvalds",
    "profile_summary": "GitHub Profile: https://github.com/torvalds\nName: Linus Torvalds\nBio: ...\nPublic Repos: 50\nFollowers: 150000\n\nTop Repositories:\n- linux (C) ⭐ 100000\n..."
  }
}
```

---

### Candidate Research
```
POST /api/research/candidate
```

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "github": "janedoe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "Jane Doe",
    "linkedin": "LinkedIn profile information...",
    "github": "GitHub profile information...",
    "web_presence": [
      {
        "title": "Result title",
        "url": "https://example.com",
        "snippet": "..."
      }
    ]
  }
}
```

---

### Company Research
```
POST /api/research/company
```

**Request:**
```json
{
  "company_name": "Google"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "Google",
    "info": [
      {
        "title": "About Google",
        "url": "https://about.google",
        "snippet": "..."
      }
    ]
  }
}
```

---

### Research Status
```
GET /api/research/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "web-research",
    "status": "operational",
    "apis": {
      "serper": true,
      "github": true
    },
    "features": [
      "web_search",
      "linkedin_lookup",
      "github_lookup",
      "candidate_research",
      "company_research"
    ]
  }
}
```

## Setup Instructions

### 1. Get Serper AI API Key

1. Visit [https://serper.dev/](https://serper.dev/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Serper Free tier includes:
   - 100 free searches per month
   - Access to Google Search API
   - Perfect for small-scale testing

### 2. Configure API Key

Add the API key to `.env` file:

```env
# Serper AI API Configuration (for web research, LinkedIn & GitHub lookups)
# Get your API key from https://serper.dev/
SERPER_API_KEY=your_api_key_here
```

### 3. Restart the Server

```bash
# From the project root
cd /home/labuser/interview_agent/interview_agent
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

Check research service status:

```bash
curl -s http://localhost:8000/api/research/status | python -m json.tool
```

Expected response shows all APIs operational.

## Usage Examples

### Example 1: Search for a Candidate on LinkedIn

```bash
curl -s -X POST http://localhost:8000/api/research/linkedin \
  -H "Content-Type: application/json" \
  -d '{"name": "Sarah Johnson", "company": "Meta"}' | python -m json.tool
```

### Example 2: Get GitHub Profile

```bash
curl -s -X POST http://localhost:8000/api/research/github \
  -H "Content-Type: application/json" \
  -d '{"username_or_name": "gvanrossum"}' | python -m json.tool
```

### Example 3: Full Candidate Research

```bash
curl -s -X POST http://localhost:8000/api/research/candidate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex Chen",
    "email": "alex@example.com",
    "github": "alexchen"
  }' | python -m json.tool
```

### Example 4: Search for Company

```bash
curl -s -X POST http://localhost:8000/api/research/company \
  -H "Content-Type: application/json" \
  -d '{"company_name": "OpenAI"}' | python -m json.tool
```

## Integration with Interview Flow

The research feature integrates seamlessly with the interview system:

### Pre-Interview Research
```python
# Research candidate before interview starts
candidate_research = await research_candidate(
    name="John Smith",
    github="johnsmith"
)

# Use research data to tailor interview questions
```

### Interview Context
```python
# LinkedIn insights about candidate's experience
# GitHub projects to discuss during technical round
# Web presence for company alignment questions
```

### Post-Interview Analysis
```python
# Verify candidate credentials
# Cross-reference with online profiles
# Assess technical background from GitHub
```

## Rate Limits

### Serper API
- **Free Plan**: 100 searches/month
- **Pro Plan**: Unlimited searches
- Rate limit: Contact support for details

### GitHub API
- **Unauthenticated**: 60 requests/hour per IP
- **Authenticated**: 5,000 requests/hour per user

## Error Handling

The research service gracefully handles:
- Missing API keys (returns empty results with warning)
- Network timeouts (10-second timeout per request)
- Invalid queries (400 Bad Request)
- API failures (500 Internal Server Error with details)

## Privacy & Ethics

### Data Handling
- All searches are performed using publicly available APIs
- No data is stored beyond the API response
- Results are read-only, no profile modifications
- Complies with LinkedIn and GitHub ToS (public profile data only)

### Best Practices
1. **Candidate Consent**: Inform candidates about research
2. **Fair Use**: Use research data for legitimate hiring purposes only
3. **Privacy Compliance**: Follow GDPR, CCPA, and local regulations
4. **Transparency**: Disclose data collection and usage

## Troubleshooting

### Issue: "Serper API key not configured"
**Solution**: Add SERPER_API_KEY to .env file and restart server

### Issue: "No LinkedIn profile found"
**Possible Causes**:
- Profile is private
- Name is too common or vague
- Try with company name included

### Issue: "No GitHub profile found"
**Possible Causes**:
- Username doesn't exist
- Try with full name instead of username
- Check GitHub profile URL manually

### Issue: Rate limit exceeded
**Solution**: 
- Use free tier carefully (100/month)
- Upgrade Serper plan for production
- Implement request caching

## Performance Optimization

### Caching Strategy
```python
# Consider caching research results to reduce API calls
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_cached_research(candidate_id: str):
    # Results cached for same candidate
    return await research_candidate(candidate_id)
```

### Batch Processing
```python
# Process multiple candidates efficiently
candidates = ["John", "Jane", "Alex"]
results = await asyncio.gather(
    *[research_candidate(name) for name in candidates]
)
```

## Future Enhancements

1. **LinkedIn Official API** (when available)
   - More detailed profile information
   - Connection status
   - Endorsements and recommendations

2. **Twitter/X Integration**
   - Professional presence
   - Technical content sharing
   - Community involvement

3. **Personal Website Scraping**
   - Portfolio analysis
   - Technical writing
   - Project showcases

4. **Stack Overflow Integration**
   - Technical expertise
   - Community contributions
   - Reputation scores

## Support

For issues or feature requests:
1. Check the troubleshooting section
2. Review Serper API documentation: https://serper.dev/docs
3. Check GitHub API documentation: https://docs.github.com/en/rest
4. Contact support through project repository

---

**Last Updated**: January 23, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
