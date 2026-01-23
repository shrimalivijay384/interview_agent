"""
Database utility functions for accessing JD and CV data.
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = Path(__file__).parent / "interview_agent.db"


def get_db_connection():
    """Get a connection to the SQLite database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Please run init_db.py first.")
    return sqlite3.connect(str(DB_PATH))


def get_jd_by_id(jd_id: int) -> Optional[Dict]:
    """Retrieve a job description by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, company, jd_content, created_at
        FROM job_descriptions WHERE id = ?
    """, (jd_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "title": row[1],
        "company": row[2],
        "content": json.loads(row[3]),
        "created_at": row[4]
    }


def get_candidate_by_id(candidate_id: int) -> Optional[Dict]:
    """Retrieve a candidate CV by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, email, cv_content, created_at
        FROM candidates WHERE id = ?
    """, (candidate_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "content": json.loads(row[3]),
        "created_at": row[4]
    }


def list_all_jds() -> List[Dict]:
    """Retrieve all job descriptions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, company, jd_content, created_at
        FROM job_descriptions
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "content": json.loads(row[3]),
            "created_at": row[4]
        }
        for row in rows
    ]


def list_all_candidates() -> List[Dict]:
    """Retrieve all candidates."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, email, cv_content, created_at
        FROM candidates
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "content": json.loads(row[3]),
            "created_at": row[4]
        }
        for row in rows
    ]


def get_db_stats() -> Dict:
    """Get statistics about the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM job_descriptions")
    jd_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM candidates")
    candidate_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_jds": jd_count,
        "total_candidates": candidate_count,
        "db_path": str(DB_PATH)
    }
