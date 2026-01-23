# Web Research API Reference

## Base URL

```
http://localhost:8000/api/research
```

## Authentication

All endpoints use API key authentication via environment variable:
```env
SERPER_API_KEY=d5b43a6ce43430805cc5d95c2d5a0ec01e2a9f80
```

No additional authentication headers required for client requests.

---

## Endpoints

### 1. GET `/status`

Check if research service is operational and configured.

**Response**:
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
  },
  "error": null
}
```

**Curl Example**:
```bash
curl http://localhost:8000/api/research/status
```

---

### 2. POST `/web-search`

Perform a general web search using Serper API.

**Request Body**:
```json
{
  "query": "machine learning engineer",
  "num_results": 5
}
```

**Parameters**:
- `query` (string, required): Search query (min 2 chars)
- `num_results` (integer, optional): Number of results to return (1-10, default: 5)

**Response**:
```json
{
  "success": true,
  "data": {
    "query": "machine learning engineer",
    "results": [
      {
        "title": "What Is a Machine Learning Engineer?",
        "url": "https://example.com/article",
        "snippet": "Machine learning engineers are critical members...",
        "source": "serper"
      }
    ]
  },
  "error": null
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/research/web-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "senior software engineer requirements",
    "num_results": 5
  }'
```

**Error Response** (if query < 2 chars):
```json
{
  "detail": "Query must be at least 2 characters"
}
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Invalid query
- `500`: API error

---

### 3. POST `/linkedin`

Search for LinkedIn profile information.

**Request Body**:
```json
{
  "name": "John Smith",
  "company": "Google"
}
```

**Parameters**:
- `name` (string, required): Candidate name (min 2 chars)
- `company` (string, optional): Company name for better matching

**Response (Found)**:
```json
{
  "success": true,
  "data": {
    "name": "John Smith",
    "company": "Google",
    "profile_summary": "LinkedIn profile found: https://linkedin.com/in/johnsmith\nPreview: Senior Software Engineer at Google..."
  },
  "error": null
}
```

**Response (Not Found)**:
```json
{
  "success": true,
  "data": {
    "name": "John Smith",
    "company": "Google",
    "profile_summary": null,
    "message": "No LinkedIn profile found"
  },
  "error": null
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/research/linkedin \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Johnson",
    "company": "Meta"
  }'
```

**HTTP Status Codes**:
- `200`: Success (found or not found)
- `400`: Invalid name
- `500`: API error

---

### 4. POST `/github`

Search for GitHub profile information.

**Request Body**:
```json
{
  "username_or_name": "torvalds"
}
```

**Parameters**:
- `username_or_name` (string, required): GitHub username or name (min 2 chars)

**Response (Found)**:
```json
{
  "success": true,
  "data": {
    "username": "torvalds",
    "profile_summary": "GitHub Profile: https://github.com/torvalds\nName: Linus Torvalds\nBio: None\nPublic Repos: 11\nFollowers: 279841\nFollowing: 0\n\nTop Repositories:\n- linux (C) ⭐ 214988\n- AudioNoise (C) ⭐ 4047\n"
  },
  "error": null
}
```

**Response (Not Found)**:
```json
{
  "success": true,
  "data": {
    "username": "nonexistentuser",
    "profile_summary": null,
    "message": "No GitHub profile found"
  },
  "error": null
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/research/github \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_name": "octocat"
  }'
```

**Response Structure (if found)**:
```
GitHub Profile: [URL]
Name: [Full Name]
Bio: [Bio text]
Public Repos: [count]
Followers: [count]
Following: [count]

Top Repositories:
- [repo_name] ([language]) ⭐ [stars]
- [repo_name] ([language]) ⭐ [stars]
...
```

**HTTP Status Codes**:
- `200`: Success (found or not found)
- `400`: Invalid username
- `500`: API error

---

### 5. POST `/candidate`

Comprehensive candidate research across all platforms.

**Request Body**:
```json
{
  "name": "Sarah Johnson",
  "email": "sarah@example.com",
  "github": "sjohnson"
}
```

**Parameters**:
- `name` (string, required): Candidate name (min 2 chars)
- `email` (string, optional): Email address
- `github` (string, optional): GitHub username

**Response**:
```json
{
  "success": true,
  "data": {
    "name": "Sarah Johnson",
    "linkedin": "LinkedIn profile found: https://linkedin.com/in/...\nPreview: ...",
    "github": "GitHub Profile: https://github.com/sjohnson\nName: Samuel Johnson\n...",
    "web_presence": [
      {
        "title": "Sarah Johnson - Software Engineer",
        "url": "https://sarahj.com",
        "snippet": "Full-stack engineer with 5+ years experience..."
      },
      {
        "title": "Sarah Johnson - LinkedIn",
        "url": "https://linkedin.com/in/sarahjohnson",
        "snippet": "Senior Software Engineer at Facebook..."
      }
    ]
  },
  "error": null
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/research/candidate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex Chen",
    "email": "alex@example.com",
    "github": "alexchen"
  }'
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Invalid name
- `500`: API error

---

### 6. POST `/company`

Research company information.

**Request Body**:
```json
{
  "company_name": "Google"
}
```

**Parameters**:
- `company_name` (string, required): Company name (min 2 chars)

**Response**:
```json
{
  "success": true,
  "data": {
    "name": "Google",
    "info": [
      {
        "title": "About Google",
        "url": "https://about.google",
        "snippet": "Google's mission is to organize the world's information..."
      },
      {
        "title": "Google Careers",
        "url": "https://careers.google.com",
        "snippet": "Join our diverse team and help shape the future..."
      }
    ]
  },
  "error": null
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/research/company \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "OpenAI"
  }'
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Invalid company name
- `500`: API error

---

## Response Format

All endpoints follow consistent response format:

```json
{
  "success": boolean,
  "data": {
    // endpoint-specific data
  },
  "error": null | string
}
```

**Fields**:
- `success` (boolean): Whether request was successful
- `data` (object): Response data (structure varies by endpoint)
- `error` (null | string): Error message if request failed

---

## Error Handling

### Common Error Scenarios

**1. Missing API Key**
```json
{
  "success": true,
  "data": {
    "results": [],
    "message": "Serper API key not configured"
  }
}
```

**2. Invalid Input**
```json
{
  "detail": "Query must be at least 2 characters"
}
```

**3. API Timeout**
```json
{
  "detail": "Search failed: Request timeout"
}
```

**4. Rate Limit**
```json
{
  "detail": "Search failed: Rate limit exceeded"
}
```

---

## Rate Limiting

### Serper API
- **Free Plan**: 100 searches/month
- **Pro Plan**: Unlimited searches
- **Rate**: No per-minute limit on free plan

### GitHub API
- **Unauthenticated**: 60 requests/hour per IP
- **Authenticated**: 5,000 requests/hour per user
- **Reset**: Hourly

---

## Usage Patterns

### Pattern 1: Pre-Interview Research
```python
# Get candidate profile
GET /api/research/status

# Research candidate
POST /api/research/candidate
{
  "name": "John Smith",
  "github": "jsmith"
}

# Research company
POST /api/research/company
{
  "company_name": "TechCorp"
}
```

### Pattern 2: Batch Candidate Research
```python
for candidate in candidates:
    POST /api/research/candidate
    {
      "name": candidate.name,
      "github": candidate.github
    }
```

### Pattern 3: Quick GitHub Check
```python
# Just check GitHub
POST /api/research/github
{
  "username_or_name": "candidate_username"
}
```

### Pattern 4: Talent Search
```python
# Search for talent in specific area
POST /api/research/web-search
{
  "query": "machine learning engineer san francisco",
  "num_results": 10
}
```

---

## Performance Considerations

### Average Response Times
- Web Search: 1-2 seconds
- GitHub Lookup: 200-500ms
- LinkedIn Lookup: 1-2 seconds
- Candidate Research: 3-5 seconds
- Company Research: 1-2 seconds

### Optimization Tips
1. Cache frequent searches
2. Use GitHub lookups for speed (no external calls)
3. Combine multiple queries efficiently
4. Implement request queuing for batch operations

---

## Integration Examples

### Example 1: Python with Requests
```python
import requests

response = requests.post(
    'http://localhost:8000/api/research/candidate',
    json={
        'name': 'John Smith',
        'github': 'jsmith'
    }
)
data = response.json()
if data['success']:
    print(f"LinkedIn: {data['data']['linkedin']}")
    print(f"GitHub: {data['data']['github']}")
```

### Example 2: JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/api/research/github', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username_or_name: 'octocat' })
});
const data = await response.json();
console.log(data.data.profile_summary);
```

### Example 3: React Component
```javascript
function CandidateResearch({ candidateName }) {
  const [research, setResearch] = useState(null);

  useEffect(() => {
    fetch('/api/research/candidate', {
      method: 'POST',
      body: JSON.stringify({ name: candidateName })
    })
    .then(r => r.json())
    .then(data => setResearch(data.data));
  }, [candidateName]);

  return <div>{research?.linkedin}</div>;
}
```

---

## Testing

### Test All Endpoints
```bash
# Status
curl http://localhost:8000/api/research/status

# Web Search
curl -X POST http://localhost:8000/api/research/web-search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI engineer", "num_results": 3}'

# GitHub
curl -X POST http://localhost:8000/api/research/github \
  -H "Content-Type: application/json" \
  -d '{"username_or_name": "torvalds"}'

# LinkedIn
curl -X POST http://localhost:8000/api/research/linkedin \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith"}'

# Candidate
curl -X POST http://localhost:8000/api/research/candidate \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "github": "janedoe"}'

# Company
curl -X POST http://localhost:8000/api/research/company \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Google"}'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 404 on endpoint | Ensure server running on port 8000 |
| Invalid JSON | Check JSON format in request body |
| Empty results | Try different search terms |
| Rate limit error | Wait for hour to reset (GitHub) |
| Timeout | Increase timeout or try again |
| No API key error | Add SERPER_API_KEY to .env |

---

## API Changelog

### Version 1.0.0 (January 23, 2026)
- Initial release
- 6 endpoints
- Serper API integration
- GitHub API integration
- Full documentation

---

## Support

- **Documentation**: See WEB_RESEARCH_GUIDE.md
- **Issues**: Check GitHub repository
- **Serper Docs**: https://serper.dev/docs
- **GitHub API**: https://docs.github.com/en/rest

---

**Last Updated**: January 23, 2026  
**Version**: 1.0.0
