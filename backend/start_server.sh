#!/bin/bash

# Interview Agent Startup Script

echo "Starting Interview Agent Backend..."

# Set environment variables
export PYTHONPATH=/home/labuser/interview_agent/interview_agent/backend:$PYTHONPATH
cd /home/labuser/interview_agent/interview_agent/backend

# Load environment variables
export GEMINI_API_KEY="AIzaSyDeF0GTiaE0dULNMMmMj9NVYEZ7gTGoo5I"
export SERPER_API_KEY="3ad4c25460c9d6f33235c5f9750cc666e503f6ca"
export ENVIRONMENT="development"
export LOG_LEVEL="INFO"

# Start uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
