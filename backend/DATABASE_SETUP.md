# SQLite Database Setup - Summary

## Created Structure

### Database Files
- **Location**: `/backend/database/interview_agent.db`
- **Framework**: SQLite3

### Database Tables

#### 1. `job_descriptions` Table
Stores job descriptions in JSON format

**Schema:**
```sql
- id (INTEGER, PRIMARY KEY)
- title (TEXT) - Job title
- company (TEXT) - Company name
- jd_content (TEXT) - Full JD in JSON format
- created_at (TIMESTAMP) - Creation timestamp
```

**Dummy Data:** 1 Senior Software Engineer position

#### 2. `candidates` Table
Stores candidate CVs in JSON format

**Schema:**
```sql
- id (INTEGER, PRIMARY KEY)
- name (TEXT) - Candidate name
- email (TEXT) - Email address
- cv_content (TEXT) - Full CV in JSON format
- created_at (TIMESTAMP) - Creation timestamp
```

**Dummy Data:** 4 Candidates
- John Smith (Senior Backend Engineer - 6 years)
- Sarah Johnson (Full-stack Engineer - 4 years)
- Michael Chen (Backend Architect - 7 years)
- Emily Davis (Backend Developer - 3 years)

## Data Format

### Job Description JSON Structure
```json
{
  "job_title": "Senior Software Engineer",
  "company": "TechCorp Solutions",
  "location": "San Francisco, CA (Remote)",
  "employment_type": "Full-time",
  "experience_required": "5+ years",
  "salary_range": "$150,000 - $200,000",
  "job_summary": "...",
  "responsibilities": [...],
  "required_skills": [...],
  "preferred_skills": [...],
  "benefits": [...]
}
```

### Candidate CV JSON Structure
```json
{
  "name": "John Smith",
  "email": "john.smith@email.com",
  "phone": "+1-555-0101",
  "summary": "...",
  "experience": [
    {
      "title": "Senior Backend Engineer",
      "company": "DataFlow Inc",
      "duration": "2021 - Present",
      "description": "..."
    }
  ],
  "education": [...],
  "skills": [...],
  "certifications": [...],
  "projects": [...]
}
```

## Usage

### View Database Contents
```bash
cd backend
python view_db.py
```

### Get Database Statistics
```python
from database import get_db_stats
stats = get_db_stats()
print(stats)  # {'total_jds': 1, 'total_candidates': 4, ...}
```

### Retrieve Data Programmatically
```python
from database import get_jd_by_id, get_candidate_by_id, list_all_candidates, list_all_jds

# Get specific JD
jd = get_jd_by_id(1)
print(jd['content'])  # Returns parsed JSON

# Get specific candidate
candidate = get_candidate_by_id(1)
print(candidate['content'])  # Returns parsed JSON

# List all
jds = list_all_jds()
candidates = list_all_candidates()
```

## Re-initialize Database
```bash
python database/init_db.py
```

This will:
1. Remove existing database
2. Create fresh tables
3. Insert dummy data
4. Display creation summary

## Next Steps
The database is now ready to be used with the KPI Determiner feature!
