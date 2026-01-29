"""
RAG (Retrieval-Augmented Generation) API Routes

Endpoints for vector search and knowledge base management
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.rag_knowledge_base import get_rag_knowledge_base

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rag", tags=["rag"])


# ==================== REQUEST/RESPONSE MODELS ====================

class SearchCandidatesRequest(BaseModel):
    """Request to search similar candidates"""
    query: str
    n_results: int = 5


class SearchQuestionsRequest(BaseModel):
    """Request to search interview questions"""
    skills: List[str]
    category: Optional[str] = None
    difficulty: Optional[str] = None
    n_results: int = 10


class AddQuestionRequest(BaseModel):
    """Request to add interview question"""
    question: str
    category: str
    skills: List[str]
    difficulty: str = "medium"


class SearchHistoryRequest(BaseModel):
    """Request to search interview history"""
    query: str
    n_results: int = 5


class AddCompanyContextRequest(BaseModel):
    """Request to add company context"""
    context_type: str  # policy, culture, value, guideline
    title: str
    content: str


class SearchCompanyContextRequest(BaseModel):
    """Request to search company context"""
    query: str
    context_type: Optional[str] = None
    n_results: int = 3


# ==================== ENDPOINTS ====================

@router.get("/stats")
async def get_rag_stats():
    """Get RAG knowledge base statistics"""
    try:
        rag = get_rag_knowledge_base()
        stats = rag.get_collection_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CANDIDATE SEARCH ====================

@router.post("/candidates/search")
async def search_similar_candidates(request: SearchCandidatesRequest):
    """
    Search for similar candidates using vector similarity
    
    Example:
    ```
    POST /api/rag/candidates/search
    {
        "query": "Python developer with AWS and Docker experience",
        "n_results": 5
    }
    ```
    """
    try:
        rag = get_rag_knowledge_base()
        results = rag.search_similar_candidates(
            query=request.query,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/candidates/sync")
async def sync_candidates_to_rag():
    """
    Sync all uploaded CVs to RAG vector store
    
    This will process all CVs in the data/cvs directory and add them to the RAG system
    """
    try:
        import os
        import json
        from pathlib import Path
        
        rag = get_rag_knowledge_base()
        cv_dir = Path(__file__).parent.parent.parent / "data" / "cvs"
        
        if not cv_dir.exists():
            return {"success": True, "message": "No CVs directory found", "count": 0}
        
        synced_count = 0
        errors = []
        
        for cv_file in cv_dir.glob("*.json"):
            try:
                with open(cv_file, 'r') as f:
                    cv_data = json.load(f)
                
                cv_id = cv_file.stem  # filename without extension
                success = rag.add_candidate(cv_id, cv_data)
                
                if success:
                    synced_count += 1
                else:
                    errors.append(f"Failed to add {cv_id}")
                    
            except Exception as e:
                errors.append(f"Error processing {cv_file.name}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Synced {synced_count} candidates to RAG",
            "count": synced_count,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Error syncing candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== INTERVIEW QUESTIONS ====================

@router.post("/questions/add")
async def add_interview_question(request: AddQuestionRequest):
    """Add an interview question to the knowledge base"""
    try:
        rag = get_rag_knowledge_base()
        success = rag.add_interview_question(
            question=request.question,
            category=request.category,
            skills=request.skills,
            difficulty=request.difficulty
        )
        
        if success:
            return {
                "success": True,
                "message": "Question added successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add question")
            
    except Exception as e:
        logger.error(f"Error adding question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/search")
async def search_interview_questions(request: SearchQuestionsRequest):
    """
    Search for relevant interview questions based on skills
    
    Example:
    ```
    POST /api/rag/questions/search
    {
        "skills": ["Python", "AWS", "Docker"],
        "category": "technical",
        "difficulty": "medium",
        "n_results": 10
    }
    ```
    """
    try:
        rag = get_rag_knowledge_base()
        questions = rag.get_relevant_questions(
            skills=request.skills,
            category=request.category,
            difficulty=request.difficulty,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "skills": request.skills,
            "questions": questions,
            "count": len(questions)
        }
        
    except Exception as e:
        logger.error(f"Error searching questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/seed")
async def seed_interview_questions():
    """Seed the knowledge base with sample interview questions"""
    try:
        rag = get_rag_knowledge_base()
        
        sample_questions = [
            # Python questions
            {
                "question": "Explain the difference between lists and tuples in Python. When would you use each?",
                "category": "technical",
                "skills": ["Python"],
                "difficulty": "easy"
            },
            {
                "question": "How does Python's Global Interpreter Lock (GIL) work and what are its implications for multithreading?",
                "category": "technical",
                "skills": ["Python", "Concurrency"],
                "difficulty": "hard"
            },
            {
                "question": "Explain decorators in Python and provide a practical use case.",
                "category": "technical",
                "skills": ["Python"],
                "difficulty": "medium"
            },
            # JavaScript/React questions
            {
                "question": "What is the difference between useMemo and useCallback hooks in React?",
                "category": "technical",
                "skills": ["React", "JavaScript"],
                "difficulty": "medium"
            },
            {
                "question": "Explain event delegation in JavaScript and why it's useful.",
                "category": "technical",
                "skills": ["JavaScript"],
                "difficulty": "medium"
            },
            # AWS/Cloud questions
            {
                "question": "Describe the differences between EC2, Lambda, and ECS. When would you use each?",
                "category": "technical",
                "skills": ["AWS", "Cloud"],
                "difficulty": "medium"
            },
            {
                "question": "How would you design a scalable, highly available web application on AWS?",
                "category": "technical",
                "skills": ["AWS", "System Design"],
                "difficulty": "hard"
            },
            # Database questions
            {
                "question": "Explain the difference between SQL and NoSQL databases. Provide use cases for each.",
                "category": "technical",
                "skills": ["Databases"],
                "difficulty": "easy"
            },
            {
                "question": "What is database normalization and why is it important?",
                "category": "technical",
                "skills": ["Databases", "SQL"],
                "difficulty": "medium"
            },
            # System Design
            {
                "question": "How would you design a URL shortening service like bit.ly?",
                "category": "technical",
                "skills": ["System Design"],
                "difficulty": "hard"
            },
            # Behavioral questions
            {
                "question": "Tell me about a time when you had to debug a complex production issue. How did you approach it?",
                "category": "behavioral",
                "skills": ["Problem Solving"],
                "difficulty": "medium"
            },
            {
                "question": "Describe a situation where you had to work with a difficult team member. How did you handle it?",
                "category": "behavioral",
                "skills": ["Teamwork", "Communication"],
                "difficulty": "medium"
            },
            {
                "question": "Tell me about a time when you disagreed with a technical decision. What did you do?",
                "category": "behavioral",
                "skills": ["Communication", "Leadership"],
                "difficulty": "medium"
            },
        ]
        
        added_count = 0
        for q in sample_questions:
            success = rag.add_interview_question(**q)
            if success:
                added_count += 1
        
        return {
            "success": True,
            "message": f"Seeded {added_count} interview questions",
            "count": added_count
        }
        
    except Exception as e:
        logger.error(f"Error seeding questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== INTERVIEW HISTORY ====================

@router.post("/history/search")
async def search_interview_history(request: SearchHistoryRequest):
    """
    Search historical interview data
    
    Example:
    ```
    POST /api/rag/history/search
    {
        "query": "Python developer interviews with high scores",
        "n_results": 5
    }
    ```
    """
    try:
        rag = get_rag_knowledge_base()
        records = rag.search_interview_history(
            query=request.query,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "query": request.query,
            "records": records,
            "count": len(records)
        }
        
    except Exception as e:
        logger.error(f"Error searching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COMPANY CONTEXT ====================

@router.post("/company/add")
async def add_company_context(request: AddCompanyContextRequest):
    """Add company context (policy, culture, values)"""
    try:
        rag = get_rag_knowledge_base()
        success = rag.add_company_context(
            context_type=request.context_type,
            title=request.title,
            content=request.content
        )
        
        if success:
            return {
                "success": True,
                "message": "Company context added successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add context")
            
    except Exception as e:
        logger.error(f"Error adding company context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/company/search")
async def search_company_context(request: SearchCompanyContextRequest):
    """
    Search company context
    
    Example:
    ```
    POST /api/rag/company/search
    {
        "query": "remote work policy",
        "context_type": "policy",
        "n_results": 3
    }
    ```
    """
    try:
        rag = get_rag_knowledge_base()
        contexts = rag.get_relevant_company_context(
            query=request.query,
            context_type=request.context_type,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "query": request.query,
            "contexts": contexts,
            "count": len(contexts)
        }
        
    except Exception as e:
        logger.error(f"Error searching company context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/company/seed")
async def seed_company_context():
    """Seed the knowledge base with sample company context"""
    try:
        rag = get_rag_knowledge_base()
        
        sample_contexts = [
            {
                "context_type": "culture",
                "title": "Innovation and Learning",
                "content": "We foster a culture of continuous learning and innovation. Team members are encouraged to experiment, learn from failures, and share knowledge. We provide learning budgets, conference attendance, and dedicated time for personal development."
            },
            {
                "context_type": "culture",
                "title": "Collaboration and Teamwork",
                "content": "Collaboration is at the heart of everything we do. We believe diverse perspectives lead to better solutions. We practice pair programming, code reviews, and cross-functional team collaboration."
            },
            {
                "context_type": "policy",
                "title": "Remote Work Policy",
                "content": "We support flexible remote work arrangements. Team members can work from home or office based on their preference. We provide necessary equipment and maintain strong communication practices for distributed teams."
            },
            {
                "context_type": "policy",
                "title": "Code Review Standards",
                "content": "All code changes must be reviewed by at least one peer before merging. Reviews should focus on correctness, readability, performance, and test coverage. We aim for constructive feedback and learning opportunities."
            },
            {
                "context_type": "value",
                "title": "Customer Focus",
                "content": "We prioritize customer needs and satisfaction. Every decision should consider the impact on our users. We gather feedback regularly and iterate based on real user needs."
            },
            {
                "context_type": "value",
                "title": "Technical Excellence",
                "content": "We maintain high standards for code quality, system design, and technical practices. We invest in tooling, automation, and best practices. Technical debt is addressed proactively."
            },
        ]
        
        added_count = 0
        for ctx in sample_contexts:
            success = rag.add_company_context(**ctx)
            if success:
                added_count += 1
        
        return {
            "success": True,
            "message": f"Seeded {added_count} company contexts",
            "count": added_count
        }
        
    except Exception as e:
        logger.error(f"Error seeding company context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN ====================

@router.post("/reset/{collection_name}")
async def reset_collection(collection_name: str):
    """Reset a specific collection (admin only)"""
    try:
        valid_collections = ["candidates", "interview_questions", "interview_history", "company_context"]
        
        if collection_name not in valid_collections:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid collection. Must be one of: {', '.join(valid_collections)}"
            )
        
        rag = get_rag_knowledge_base()
        success = rag.reset_collection(collection_name)
        
        if success:
            return {
                "success": True,
                "message": f"Collection '{collection_name}' reset successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset collection")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
