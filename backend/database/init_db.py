"""
Initialize SQLite database with dummy JD and CV data in JSON format.
"""
import sqlite3
import json
import os
from pathlib import Path

# Database path
DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "interview_agent.db"


def create_tables(conn):
    """Create database tables for JDs and CVs."""
    cursor = conn.cursor()
    
    # Create job_descriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            jd_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create candidates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            cv_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("✓ Tables created successfully")


def get_dummy_jd():
    """Return a dummy Job Description in JSON format."""
    jd = {
        "job_title": "Senior Software Engineer",
        "company": "TechCorp Solutions",
        "location": "San Francisco, CA (Remote)",
        "employment_type": "Full-time",
        "experience_required": "5+ years",
        "salary_range": "$150,000 - $200,000",
        "job_summary": "We are looking for a Senior Software Engineer to join our team and lead the development of our core platform.",
        "responsibilities": [
            "Design and implement scalable microservices architecture",
            "Lead code reviews and mentor junior developers",
            "Collaborate with product and design teams to deliver features",
            "Optimize system performance and reduce latency",
            "Participate in architectural decision-making"
        ],
        "required_skills": [
            "Python 3.8+",
            "FastAPI or Django",
            "SQL and NoSQL databases",
            "AWS or GCP",
            "Docker and Kubernetes",
            "Git and CI/CD pipelines",
            "REST API design",
            "System design and architecture"
        ],
        "preferred_skills": [
            "Machine Learning experience",
            "Message queues (RabbitMQ, Kafka)",
            "MongoDB or PostgreSQL",
            "Terraform",
            "Open source contributions",
            "Agile/Scrum experience"
        ],
        "benefits": [
            "Competitive salary and equity",
            "Health insurance (medical, dental, vision)",
            "401(k) matching",
            "Remote work flexibility",
            "Professional development budget",
            "Unlimited PTO"
        ]
    }
    return jd


def get_dummy_cvs():
    """Return a list of dummy CVs in JSON format."""
    cvs = [
        {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "+1-555-0101",
            "summary": "Experienced software engineer with 6 years of experience building scalable backend systems. Passionate about clean code and system architecture.",
            "experience": [
                {
                    "title": "Senior Backend Engineer",
                    "company": "DataFlow Inc",
                    "duration": "2021 - Present",
                    "description": "Led the redesign of payment processing system using FastAPI, reducing latency by 60%"
                },
                {
                    "title": "Backend Engineer",
                    "company": "WebServices Ltd",
                    "duration": "2018 - 2021",
                    "description": "Developed REST APIs using Django and managed PostgreSQL databases for millions of users"
                },
                {
                    "title": "Junior Developer",
                    "company": "StartupXYZ",
                    "duration": "2017 - 2018",
                    "description": "Built features in Python and contributed to CI/CD pipeline improvements"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "university": "State University",
                    "year": 2017
                }
            ],
            "skills": [
                "Python", "FastAPI", "Django", "PostgreSQL", "MongoDB",
                "AWS", "Docker", "Kubernetes", "Git", "REST APIs",
                "System Design", "Microservices"
            ],
            "certifications": [
                "AWS Solutions Architect Associate"
            ],
            "projects": [
                {
                    "name": "Real-time Analytics Platform",
                    "description": "Built a real-time data analytics platform using FastAPI and Redis"
                }
            ]
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@email.com",
            "phone": "+1-555-0102",
            "summary": "Full-stack engineer with 4 years of experience. Strong in Python backend development and cloud architecture.",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "CloudTech Solutions",
                    "duration": "2020 - Present",
                    "description": "Developed microservices using FastAPI and deployed on AWS ECS"
                },
                {
                    "title": "Junior Software Engineer",
                    "company": "TechStartup",
                    "duration": "2018 - 2020",
                    "description": "Contributed to Django-based web application and wrote unit tests"
                }
            ],
            "education": [
                {
                    "degree": "Master of Science",
                    "field": "Software Engineering",
                    "university": "Tech University",
                    "year": 2018
                }
            ],
            "skills": [
                "Python", "FastAPI", "PostgreSQL", "AWS", "Docker",
                "JavaScript", "React", "Git", "Linux", "Agile"
            ],
            "certifications": [
                "AWS Developer Associate"
            ],
            "projects": [
                {
                    "name": "Order Management System",
                    "description": "Created a scalable order management system with FastAPI and PostgreSQL"
                }
            ]
        },
        {
            "name": "Michael Chen",
            "email": "m.chen@email.com",
            "phone": "+1-555-0103",
            "summary": "Backend architect with 7 years of experience in building distributed systems and leading engineering teams.",
            "experience": [
                {
                    "title": "Tech Lead",
                    "company": "EnterpriseCorps",
                    "duration": "2019 - Present",
                    "description": "Led team of 5 engineers, architected microservices platform handling 10M requests/day"
                },
                {
                    "title": "Senior Engineer",
                    "company": "FinanceFlow",
                    "duration": "2016 - 2019",
                    "description": "Built payment processing system using Python and managed database optimization"
                },
                {
                    "title": "Software Engineer",
                    "company": "WebScale",
                    "duration": "2014 - 2016",
                    "description": "Developed APIs and worked on scalability improvements"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "university": "University of Technology",
                    "year": 2014
                }
            ],
            "skills": [
                "Python", "Go", "FastAPI", "Django", "PostgreSQL", "MongoDB",
                "Redis", "AWS", "Kubernetes", "Terraform", "System Design",
                "Microservices", "Message Queues"
            ],
            "certifications": [
                "AWS Solutions Architect Professional",
                "Kubernetes Application Developer"
            ],
            "projects": [
                {
                    "name": "Distributed Payment System",
                    "description": "Designed and built a fault-tolerant payment system processing billions in transactions"
                }
            ]
        },
        {
            "name": "Emily Davis",
            "email": "emily.davis@email.com",
            "phone": "+1-555-0104",
            "summary": "Backend developer with 3 years of experience, strong foundation in Python and cloud technologies.",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "AppDevelopers Inc",
                    "duration": "2021 - Present",
                    "description": "Built REST APIs using FastAPI and optimized database queries"
                },
                {
                    "title": "Junior Developer",
                    "company": "CodeWorks",
                    "duration": "2019 - 2021",
                    "description": "Worked on Django application and wrote automated tests"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "university": "State College",
                    "year": 2019
                }
            ],
            "skills": [
                "Python", "FastAPI", "PostgreSQL", "AWS", "Docker",
                "Git", "HTML", "CSS", "JavaScript"
            ],
            "certifications": [],
            "projects": [
                {
                    "name": "User Management API",
                    "description": "Created a user management API with authentication and authorization"
                }
            ]
        }
    ]
    return cvs


def insert_dummy_data(conn):
    """Insert dummy JD and CV data into the database."""
    cursor = conn.cursor()
    
    # Insert Job Description
    jd = get_dummy_jd()
    cursor.execute("""
        INSERT INTO job_descriptions (title, company, jd_content)
        VALUES (?, ?, ?)
    """, (jd["job_title"], jd["company"], json.dumps(jd)))
    
    # Insert Candidates
    cvs = get_dummy_cvs()
    for cv in cvs:
        cursor.execute("""
            INSERT INTO candidates (name, email, cv_content)
            VALUES (?, ?, ?)
        """, (cv["name"], cv["email"], json.dumps(cv)))
    
    conn.commit()
    print(f"✓ Inserted 1 Job Description")
    print(f"✓ Inserted {len(cvs)} Candidate CVs")


def init_database():
    """Initialize database with tables and dummy data."""
    # Remove existing database if it exists (for fresh start)
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")
    
    # Create database and tables
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    insert_dummy_data(conn)
    conn.close()
    
    print(f"✓ Database initialized successfully at: {DB_PATH}")
    return DB_PATH


if __name__ == "__main__":
    init_database()
