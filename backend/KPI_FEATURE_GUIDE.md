# KPI Determiner Feature - Complete Integration Guide

## Overview

The KPI Determiner feature uses the **Google Gemini API** to automatically determine Key Performance Indicators (KPIs) for interview sessions based on:
- **Job Description (JD)**: Position requirements and responsibilities
- **Candidate CV**: Background, experience, and skills

The system is fully integrated with:
- SQLite database storing JDs and CVs in JSON format
- FastAPI backend with RESTful endpoints
- Gemini API for intelligent KPI analysis

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
├─────────────────────────────────────────────────────────┤
│  Routes: /api/kpi/*                                      │
│  ├─ POST /api/kpi/determine (Main KPI determination)    │
│  ├─ GET /api/kpi/database-info                          │
│  ├─ GET /api/kpi/jobs                                   │
│  ├─ GET /api/kpi/jobs/{id}                              │
│  ├─ GET /api/kpi/candidates                             │
│  └─ GET /api/kpi/candidates/{id}                        │
├─────────────────────────────────────────────────────────┤
│  Services: KPIDeterminer                                 │
│  ├─ determine_kpis_from_db()    (Main method)           │
│  ├─ _parse_jd_from_db()                                 │
│  ├─ _parse_cv_from_db()                                 │
│  └─ format_kpis_for_display()                           │
├─────────────────────────────────────────────────────────┤
│  Database: SQLite (interview_agent.db)                   │
│  ├─ job_descriptions table                              │
│  └─ candidates table                                     │
├─────────────────────────────────────────────────────────┤
│  External: Google Gemini API                             │
│  ├─ gemini-1.5-pro model                                │
│  └─ JSON response parsing                               │
└─────────────────────────────────────────────────────────┘
```

## Files Created/Modified

### New Files

1. **`app/services/kpi_determiner_db.py`** - Main KPI determination service
   - `KPIDeterminer` class with Gemini integration
   - Database parsing and KPI extraction
   - Response validation and normalization

2. **`app/routes/kpi.py`** - API endpoints
   - `POST /api/kpi/determine` - Main endpoint
   - `GET /api/kpi/database-info` - Database statistics
   - `GET /api/kpi/jobs` - List all JDs
   - `GET /api/kpi/jobs/{id}` - Get specific JD
   - `GET /api/kpi/candidates` - List all candidates
   - `GET /api/kpi/candidates/{id}` - Get specific candidate

3. **`test_kpi_demo.py`** - Demo/test script
   - Tests database connectivity
   - Demonstrates KPI determination
   - Tests all candidate-JD combinations

### Modified Files

1. **`app/main.py`** - Added KPI router
2. **`app/routes/__init__.py`** - Added KPI route export
3. **`database/init_db.py`** - Already has dummy data
4. **`database/db_utils.py`** - Already has query functions

## Usage

### 1. Setup Environment

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Or create a .env file in backend directory
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

### 2. Initialize Database (if not already done)

```bash
cd backend
python database/init_db.py
```

### 3. Test KPI Determination

```bash
# Run the demo script
python test_kpi_demo.py
```

### 4. Start the Backend Server

```bash
# Make sure you're in the backend directory
cd backend

# Install dependencies if needed
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Use the API

#### Get Database Info
```bash
curl http://localhost:8000/api/kpi/database-info
```

#### List All Jobs
```bash
curl http://localhost:8000/api/kpi/jobs
```

#### List All Candidates
```bash
curl http://localhost:8000/api/kpi/candidates
```

#### Determine KPIs
```bash
curl -X POST http://localhost:8000/api/kpi/determine \
  -H "Content-Type: application/json" \
  -d '{"jd_id": 1, "candidate_id": 1}'
```

## API Endpoints

### POST /api/kpi/determine
**Determine KPIs for a candidate-JD pair**

**Request:**
```json
{
  "jd_id": 1,
  "candidate_id": 1
}
```

**Response:**
```json
{
  "kpis": [
    {
      "id": "kpi_1",
      "name": "Core Technical Skills",
      "weight": 0.25,
      "description": "Proficiency in required technical skills...",
      "expected_level": "senior",
      "category": "technical"
    },
    ...
  ],
  "reasoning": "Based on the job requirements and candidate background...",
  "candidate_info": {
    "name": "John Smith",
    "email": "john.smith@email.com",
    "years_of_experience": 6,
    "experience_level": "senior"
  },
  "jd_info": {
    "title": "Senior Software Engineer",
    "company": "TechCorp Solutions"
  },
  "database_ids": {
    "jd_id": 1,
    "candidate_id": 1
  }
}
```

### GET /api/kpi/database-info
**Get database statistics**

**Query Parameters:**
- `include_data` (bool, optional): Include full JD and candidate data

**Response:**
```json
{
  "total_jds": 1,
  "total_candidates": 4,
  "db_path": "/path/to/interview_agent.db",
  "jds": [...],
  "candidates": [...]
}
```

### GET /api/kpi/jobs
**List all job descriptions**

**Response:**
```json
{
  "total": 1,
  "jobs": [
    {
      "id": 1,
      "title": "Senior Software Engineer",
      "company": "TechCorp Solutions",
      "location": "San Francisco, CA (Remote)",
      "experience_required": "5+ years",
      "created_at": "2026-01-23 06:20:30"
    }
  ]
}
```

### GET /api/kpi/jobs/{jd_id}
**Get detailed job description**

### GET /api/kpi/candidates
**List all candidates**

**Response:**
```json
{
  "total": 4,
  "candidates": [
    {
      "id": 1,
      "name": "John Smith",
      "email": "john.smith@email.com",
      "created_at": "2026-01-23 06:20:30"
    },
    ...
  ]
}
```

### GET /api/kpi/candidates/{candidate_id}
**Get detailed candidate information**

## KPI Response Structure

Each KPI contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (kpi_1, kpi_2, etc.) |
| `name` | string | Short KPI name |
| `weight` | float | Importance weight (0.0-1.0, sum=1.0) |
| `description` | string | Detailed description of what to evaluate |
| `expected_level` | string | Expected proficiency (junior, mid, senior, expert) |
| `category` | string | KPI category (technical, behavioral, problem_solving, cultural, domain) |

## Gemini API Integration

### System Prompt
The system prompt provides context to Gemini:
- Expert recruiter perspective
- KPI categorization guidelines
- Experience level definitions
- Evaluation criteria

### User Prompt
Includes:
- Parsed job description
- Parsed candidate CV
- Expected JSON output format
- Validation requirements

### Response Parsing
- Extracts JSON from response (handles markdown code blocks)
- Validates required fields
- Normalizes weights to sum to 1.0
- Returns structured KPI list with reasoning

## Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your-gemini-api-key

# Optional (defaults provided)
GEMINI_MODEL=gemini-1.5-pro          # or gemini-pro
GEMINI_TEMPERATURE=0.7               # 0.0-1.0, lower = more deterministic
GEMINI_MAX_TOKENS=2048               # Max response length
```

### Model Configuration (in `app/config.py`)

```python
# Defaults
gemini_model: str = "gemini-pro"
gemini_temperature: float = 0.7
gemini_max_tokens: int = 2048
```

## Example: Full KPI Determination Flow

```python
from app.services.kpi_determiner_db import get_kpi_determiner
import asyncio

async def main():
    # Get the KPI determiner
    kpi_determiner = get_kpi_determiner()
    
    # Determine KPIs
    result = await kpi_determiner.determine_kpis_from_db(
        jd_id=1,
        candidate_id=1
    )
    
    # Display results
    print(kpi_determiner.format_kpis_for_display(result))
    
    # Access individual components
    print(f"Candidate: {result['candidate_info']['name']}")
    print(f"Position: {result['jd_info']['title']}")
    print(f"Number of KPIs: {len(result['kpis'])}")
    
    for kpi in result['kpis']:
        print(f"- {kpi['name']} ({kpi['weight']*100:.1f}%)")

asyncio.run(main())
```

## Error Handling

### Common Errors

1. **FileNotFoundError**: Database not initialized
   - Solution: Run `python database/init_db.py`

2. **ValueError**: Invalid JD/Candidate ID
   - Check ID exists: `GET /api/kpi/database-info?include_data=true`

3. **API Key Error**: GEMINI_API_KEY not set
   - Set environment variable or .env file

4. **JSON Parse Error**: Invalid Gemini response
   - Check logs for full response
   - May need to adjust temperature/model

## Testing

### Run Demo Script
```bash
cd backend
python test_kpi_demo.py
```

### Run Unit Tests (if available)
```bash
pytest tests/test_kpi_determiner_db.py -v
```

### Manual API Testing
```bash
# Get database info
curl http://localhost:8000/api/kpi/database-info

# Determine KPIs
curl -X POST http://localhost:8000/api/kpi/determine \
  -H "Content-Type: application/json" \
  -d '{"jd_id": 1, "candidate_id": 1}' | jq .
```

## Logging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Logs include:
- KPI determination start/completion
- Database queries
- Gemini API calls
- JSON parsing details
- Error traces

## Performance Considerations

### Database Queries
- O(1) lookup by ID
- Simple table scans for list operations
- SQLite suitable for small-medium datasets

### Gemini API
- ~2-5 seconds per determination request
- Rate limits apply (check Gemini documentation)
- Costs based on tokens used

### Optimization Tips
1. Cache frequently used JD-Candidate combinations
2. Batch API calls when possible
3. Use appropriate temperature setting
4. Monitor token usage

## Future Enhancements

1. **Caching**: Store KPI determinations for same JD-Candidate pairs
2. **Batch Processing**: Determine KPIs for multiple candidates at once
3. **Feedback Loop**: Refine KPIs based on interview results
4. **Custom Models**: Support custom Gemini model versions
5. **Database Export**: Export KPIs to CSV/PDF
6. **Interview Session Storage**: Link KPIs to interview sessions

## Troubleshooting

### KPIs Not Generated
- Check GEMINI_API_KEY is set correctly
- Verify internet connectivity
- Check Gemini API status

### Database Empty
- Run: `python database/init_db.py`
- Verify DB file exists: `ls -la database/interview_agent.db`

### Weights Don't Sum to 1.0
- API automatically normalizes weights
- Check logs for normalization details

### API Timeout
- Increase timeout in FastAPI settings
- Check Gemini API response times
- Reduce max_tokens if too high

## Support

For issues or questions:
1. Check logs: `tail -f app.log`
2. Verify database: `python database/view_db.py`
3. Test API: `curl http://localhost:8000/api/kpi/database-info`
