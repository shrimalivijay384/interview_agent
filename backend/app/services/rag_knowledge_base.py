"""
RAG (Retrieval-Augmented Generation) System for Interview Agent

This module provides vector search and knowledge base management for:
1. CV database (search similar candidates)
2. Interview questions knowledge base
3. Historical interview data
4. Company policy and culture context
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import hashlib

logger = logging.getLogger(__name__)


class RAGKnowledgeBase:
    """
    RAG Knowledge Base for Interview Agent
    
    Collections:
    - candidates: Vector store of all CVs for similarity search
    - interview_questions: Knowledge base of interview questions by topic/skill
    - interview_history: Historical interview sessions with outcomes
    - company_context: Company policies, culture, values for context
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """Initialize RAG system with ChromaDB"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model (sentence-transformers)
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded successfully")
        
        # Initialize collections
        self._init_collections()
        
        logger.info("RAG Knowledge Base initialized")
    
    def _init_collections(self):
        """Initialize or get existing collections"""
        try:
            # Candidates collection (CVs)
            self.candidates_collection = self.client.get_or_create_collection(
                name="candidates",
                metadata={"description": "Vector store of candidate CVs"}
            )
            
            # Interview questions collection
            self.questions_collection = self.client.get_or_create_collection(
                name="interview_questions",
                metadata={"description": "Knowledge base of interview questions"}
            )
            
            # Interview history collection
            self.history_collection = self.client.get_or_create_collection(
                name="interview_history",
                metadata={"description": "Historical interview data"}
            )
            
            # Company context collection
            self.company_collection = self.client.get_or_create_collection(
                name="company_context",
                metadata={"description": "Company policies and culture"}
            )
            
            logger.info("All collections initialized")
            
        except Exception as e:
            logger.error(f"Error initializing collections: {str(e)}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence-transformers"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def _generate_id(self, text: str, prefix: str = "") -> str:
        """Generate unique ID from text hash"""
        hash_obj = hashlib.md5(text.encode())
        return f"{prefix}{hash_obj.hexdigest()[:16]}"
    
    # ==================== CANDIDATE CV OPERATIONS ====================
    
    def add_candidate(
        self,
        cv_id: str,
        cv_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a candidate CV to the vector store
        
        Args:
            cv_id: Unique CV identifier
            cv_data: Parsed CV data
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Extract text for embedding
            name = cv_data.get("name", "Unknown")
            
            # Handle both direct and nested parsed_data structures
            if "parsed_data" in cv_data:
                parsed = cv_data["parsed_data"]
                summary = parsed.get("summary", "")
                skills_list = parsed.get("skills", [])
                work_exp = parsed.get("work_experience", [])
            else:
                summary = cv_data.get("summary", "")
                skills_list = cv_data.get("skills", [])
                work_exp = cv_data.get("work_experience", [])
            
            # Build searchable text
            skills_text = ", ".join(skills_list) if isinstance(skills_list, list) else str(skills_list)
            
            # Extract work experience text
            work_text = ""
            if work_exp and isinstance(work_exp, list):
                for exp in work_exp[:3]:  # Top 3 positions
                    if isinstance(exp, dict):
                        title = exp.get("title", "")
                        company = exp.get("company", "")
                        work_text += f"{title} at {company}. "
            
            # Combine for embedding
            searchable_text = f"{name}. {summary}. Skills: {skills_text}. Experience: {work_text}"
            
            # Generate embedding
            embedding = self._generate_embedding(searchable_text)
            
            # Prepare metadata
            meta = {
                "cv_id": cv_id,
                "name": name,
                "added_at": datetime.utcnow().isoformat(),
                "skills": skills_text[:500],  # Truncate for metadata
                "summary": summary[:200] if summary else ""
            }
            if metadata:
                meta.update(metadata)
            
            # Add to collection
            self.candidates_collection.add(
                ids=[cv_id],
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[meta]
            )
            
            logger.info(f"Added candidate {cv_id} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding candidate: {str(e)}")
            return False
    
    def search_similar_candidates(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar candidates based on query
        
        Args:
            query: Search query (skills, experience, etc.)
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar candidates with scores
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search
            results = self.candidates_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            candidates = []
            if results and results['ids']:
                for i, cv_id in enumerate(results['ids'][0]):
                    candidates.append({
                        "cv_id": cv_id,
                        "similarity_score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "metadata": results['metadatas'][0][i],
                        "document": results['documents'][0][i]
                    })
            
            logger.info(f"Found {len(candidates)} similar candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error searching candidates: {str(e)}")
            return []
    
    # ==================== INTERVIEW QUESTIONS OPERATIONS ====================
    
    def add_interview_question(
        self,
        question: str,
        category: str,
        skills: List[str],
        difficulty: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an interview question to the knowledge base
        
        Args:
            question: The interview question text
            category: Category (technical, behavioral, situational, etc.)
            skills: Related skills/technologies
            difficulty: easy, medium, hard
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            question_id = self._generate_id(question, "q_")
            
            # Generate embedding
            searchable_text = f"{category}. {', '.join(skills)}. {question}"
            embedding = self._generate_embedding(searchable_text)
            
            # Prepare metadata
            meta = {
                "category": category,
                "skills": json.dumps(skills),
                "difficulty": difficulty,
                "added_at": datetime.utcnow().isoformat()
            }
            if metadata:
                meta.update(metadata)
            
            # Add to collection
            self.questions_collection.add(
                ids=[question_id],
                embeddings=[embedding],
                documents=[question],
                metadatas=[meta]
            )
            
            logger.info(f"Added interview question: {question_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding question: {str(e)}")
            return False
    
    def get_relevant_questions(
        self,
        skills: List[str],
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant interview questions based on skills
        
        Args:
            skills: List of skills to match
            category: Optional category filter
            difficulty: Optional difficulty filter
            n_results: Number of questions to return
            
        Returns:
            List of relevant questions
        """
        try:
            # Build query
            query = f"Questions about {', '.join(skills)}"
            query_embedding = self._generate_embedding(query)
            
            # Build filters
            where_filter = {}
            if category:
                where_filter["category"] = category
            if difficulty:
                where_filter["difficulty"] = difficulty
            
            # Search
            results = self.questions_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            questions = []
            if results and results['ids']:
                for i, q_id in enumerate(results['ids'][0]):
                    questions.append({
                        "question_id": q_id,
                        "question": results['documents'][0][i],
                        "relevance_score": 1 - results['distances'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
            
            logger.info(f"Retrieved {len(questions)} relevant questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error retrieving questions: {str(e)}")
            return []
    
    # ==================== INTERVIEW HISTORY OPERATIONS ====================
    
    def add_interview_record(
        self,
        session_id: str,
        candidate_name: str,
        job_title: str,
        interview_data: Dict[str, Any],
        outcome: Optional[str] = None
    ) -> bool:
        """
        Store historical interview data
        
        Args:
            session_id: Interview session ID
            candidate_name: Candidate name
            job_title: Job position
            interview_data: Complete interview data (questions, answers, scores)
            outcome: Final outcome (hired, rejected, pending)
            
        Returns:
            Success status
        """
        try:
            # Build searchable summary
            summary = f"Interview for {job_title} position with {candidate_name}. "
            
            # Add KPI scores if available
            if "per_kpi_scores" in interview_data:
                kpis = [kpi.get("kpi_name", "") for kpi in interview_data["per_kpi_scores"]]
                summary += f"KPIs evaluated: {', '.join(kpis)}. "
            
            # Add overall score
            if "overall_score" in interview_data:
                summary += f"Overall score: {interview_data['overall_score']}/5.0"
            
            # Generate embedding
            embedding = self._generate_embedding(summary)
            
            # Prepare metadata
            metadata = {
                "session_id": session_id,
                "candidate_name": candidate_name,
                "job_title": job_title,
                "outcome": outcome or "pending",
                "overall_score": str(interview_data.get("overall_score", 0)),
                "interview_date": datetime.utcnow().isoformat()
            }
            
            # Store full data as document
            document = json.dumps(interview_data)
            
            # Add to collection
            self.history_collection.add(
                ids=[session_id],
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata]
            )
            
            logger.info(f"Added interview history: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding interview record: {str(e)}")
            return False
    
    def search_interview_history(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search historical interview data
        
        Args:
            query: Search query
            n_results: Number of results
            filter_metadata: Optional filters
            
        Returns:
            List of relevant interview records
        """
        try:
            query_embedding = self._generate_embedding(query)
            
            results = self.history_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            records = []
            if results and results['ids']:
                for i, session_id in enumerate(results['ids'][0]):
                    try:
                        interview_data = json.loads(results['documents'][0][i])
                    except:
                        interview_data = {}
                    
                    records.append({
                        "session_id": session_id,
                        "relevance_score": 1 - results['distances'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "interview_data": interview_data
                    })
            
            logger.info(f"Found {len(records)} interview records")
            return records
            
        except Exception as e:
            logger.error(f"Error searching interview history: {str(e)}")
            return []
    
    # ==================== COMPANY CONTEXT OPERATIONS ====================
    
    def add_company_context(
        self,
        context_type: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add company context (policies, culture, values)
        
        Args:
            context_type: Type (policy, culture, value, guideline)
            title: Context title
            content: Full context content
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            context_id = self._generate_id(f"{context_type}_{title}", "ctx_")
            
            # Generate embedding
            searchable_text = f"{context_type}: {title}. {content}"
            embedding = self._generate_embedding(searchable_text)
            
            # Prepare metadata
            meta = {
                "context_type": context_type,
                "title": title,
                "added_at": datetime.utcnow().isoformat()
            }
            if metadata:
                meta.update(metadata)
            
            # Add to collection
            self.company_collection.add(
                ids=[context_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[meta]
            )
            
            logger.info(f"Added company context: {context_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding company context: {str(e)}")
            return False
    
    def get_relevant_company_context(
        self,
        query: str,
        context_type: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant company context for a query
        
        Args:
            query: Search query
            context_type: Optional context type filter
            n_results: Number of results
            
        Returns:
            List of relevant context
        """
        try:
            query_embedding = self._generate_embedding(query)
            
            where_filter = {"context_type": context_type} if context_type else None
            
            results = self.company_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            contexts = []
            if results and results['ids']:
                for i, ctx_id in enumerate(results['ids'][0]):
                    contexts.append({
                        "context_id": ctx_id,
                        "content": results['documents'][0][i],
                        "relevance_score": 1 - results['distances'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
            
            logger.info(f"Retrieved {len(contexts)} company contexts")
            return contexts
            
        except Exception as e:
            logger.error(f"Error retrieving company context: {str(e)}")
            return []
    
    # ==================== UTILITY METHODS ====================
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections"""
        try:
            return {
                "candidates_count": self.candidates_collection.count(),
                "questions_count": self.questions_collection.count(),
                "history_count": self.history_collection.count(),
                "company_context_count": self.company_collection.count(),
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}
    
    def reset_collection(self, collection_name: str) -> bool:
        """Reset a specific collection"""
        try:
            self.client.delete_collection(collection_name)
            self._init_collections()
            logger.info(f"Reset collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            return False


# Global instance
_rag_kb: Optional[RAGKnowledgeBase] = None


def get_rag_knowledge_base() -> RAGKnowledgeBase:
    """Get or create global RAG knowledge base instance"""
    global _rag_kb
    if _rag_kb is None:
        _rag_kb = RAGKnowledgeBase()
    return _rag_kb
