"""
Asking Question Agent - orchestrates the interview process.
"""
import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import (
    JobDescription, Resume, KPI, Question, Answer, QuestionAnswerPair,
    InterviewSession, InterviewStatus, FinalReport, KPIEval,
    Difficulty, QuestionType
)
from app.services.gemini_client import get_gemini_client
from app.config import get_settings

logger = logging.getLogger(__name__)


# In-memory session store
class SessionStore:
    """Simple in-memory storage for interview sessions."""
    
    def __init__(self):
        self._sessions: Dict[str, InterviewSession] = {}
    
    def create_session(self, session: InterviewSession) -> str:
        """Create a new session."""
        self._sessions[session.id] = session
        logger.info(f"Created session: {session.id}")
        return session.id
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)
    
    def update_session(self, session: InterviewSession):
        """Update an existing session."""
        session.updated_at = datetime.utcnow()
        self._sessions[session.id] = session
        logger.debug(f"Updated session: {session.id}")
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")


# Global session store
_session_store = SessionStore()


def get_session_store() -> SessionStore:
    """Get the global session store."""
    return _session_store


QUESTION_GENERATION_SYSTEM_PROMPT = """You are an expert technical interviewer. Your role is to generate thoughtful, relevant interview questions that effectively evaluate specific KPIs (Key Performance Indicators).

Guidelines for generating questions:
1. Questions should be clear, specific, and directly related to the target KPIs
2. Adjust difficulty based on the candidate's experience level
3. Mix different question types: technical, behavioral, situational, system design
4. Build upon previous answers when generating follow-up questions
5. Ensure questions are fair and unbiased
6. Make questions open-ended to encourage detailed responses
7. Consider the candidate's background from their resume

Question Types:
- technical: Coding, algorithms, technical concepts, tools
- behavioral: Past experiences, teamwork, conflict resolution
- system_design: Architecture, scalability, design decisions
- situational: Hypothetical scenarios, problem-solving
- culture: Work style, values, career goals"""


ANSWER_EVALUATION_SYSTEM_PROMPT = """You are an expert technical interviewer evaluating candidate responses. Your role is to:

1. Assess the quality and completeness of the answer
2. Score relevant KPIs on a scale of 0-5:
   - 0: No understanding or completely incorrect
   - 1: Minimal understanding, major gaps
   - 2: Basic understanding, significant gaps
   - 3: Adequate understanding, some gaps
   - 4: Good understanding, minor gaps
   - 5: Excellent understanding, comprehensive

3. Provide constructive justification for each score
4. Identify strengths and areas for improvement
5. Determine if follow-up questions are needed

Be fair, objective, and consider:
- Technical accuracy
- Depth of knowledge
- Communication clarity
- Problem-solving approach
- Real-world applicability"""


async def start_interview(
    jd: JobDescription,
    resume: Resume,
    kpis: List[KPI]
) -> InterviewSession:
    """
    Initialize a new interview session.
    
    Args:
        jd: Job description
        resume: Candidate's resume
        kpis: List of KPIs to evaluate
        
    Returns:
        New InterviewSession with first question
    """
    try:
        logger.info(f"Starting interview for {resume.name} - {jd.title}")
        
        # Create session
        session_id = str(uuid.uuid4())
        session = InterviewSession(
            id=session_id,
            jd=jd,
            resume=resume,
            kpis=kpis,
            status=InterviewStatus.INITIALIZED
        )
        
        # Initialize KPI scores
        for kpi in kpis:
            session.kpi_scores[kpi.id] = []
        
        # Generate first question
        first_question = await _generate_question(session, is_first=True)
        
        # Add to history
        session.question_history.append(
            QuestionAnswerPair(question=first_question)
        )
        session.status = InterviewStatus.IN_PROGRESS
        
        # Store session
        store = get_session_store()
        store.create_session(session)
        
        logger.info(f"Interview started: {session_id}")
        return session
        
    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}")
        raise


async def get_next_question(
    session_id: str,
    answer_text: str,
    duration_seconds: Optional[float] = None
) -> tuple[Optional[Question], bool, List[KPIEval]]:
    """
    Process an answer and generate the next question.
    
    Args:
        session_id: Interview session ID
        answer_text: Candidate's answer text
        duration_seconds: Time taken to answer
        
    Returns:
        Tuple of (next_question, is_complete, evaluations)
    """
    try:
        store = get_session_store()
        session = store.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Get current question
        current_question = session.get_current_question()
        if not current_question:
            raise ValueError("No active question in session")
        
        # Create answer object
        answer = Answer(
            question_id=current_question.id,
            text=answer_text,
            duration_seconds=duration_seconds
        )
        
        # Evaluate the answer
        evaluations = await _evaluate_answer(session, current_question, answer)
        
        # Update session with answer and evaluations
        session.question_history[-1].answer = answer
        session.question_history[-1].evaluations = evaluations
        
        # Update KPI scores
        for eval in evaluations:
            session.add_kpi_score(eval.kpi_id, eval.score)
        
        # Check if interview should continue
        settings = get_settings()
        question_count = len(session.question_history)
        
        should_continue = (
            question_count < settings.max_questions_per_interview and
            _should_ask_more_questions(session)
        )
        
        next_question = None
        is_complete = not should_continue
        
        if should_continue:
            # Generate next question
            next_question = await _generate_question(session)
            session.question_history.append(
                QuestionAnswerPair(question=next_question)
            )
        else:
            # Mark as complete
            session.status = InterviewStatus.COMPLETED
        
        # Update session
        store.update_session(session)
        
        return next_question, is_complete, evaluations
        
    except Exception as e:
        logger.error(f"Error getting next question: {str(e)}")
        raise


async def finalize_interview(session_id: str) -> FinalReport:
    """
    Generate final report for completed interview.
    
    Args:
        session_id: Interview session ID
        
    Returns:
        FinalReport with scores and feedback
    """
    try:
        store = get_session_store()
        session = store.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        logger.info(f"Finalizing interview: {session_id}")
        
        # Calculate per-KPI scores
        per_kpi_scores = []
        for kpi in session.kpis:
            avg_score = session.get_average_kpi_score(kpi.id)
            per_kpi_scores.append(
                KPIEval(
                    kpi_id=kpi.id,
                    score=avg_score,
                    justification=f"{kpi.name}: Average score based on {len(session.kpi_scores.get(kpi.id, []))} evaluations"
                )
            )
        
        # Calculate weighted overall score
        overall_score = sum(
            eval.score * next((k.weight for k in session.kpis if k.id == eval.kpi_id), 0)
            for eval in per_kpi_scores
        )
        
        # Generate detailed analysis with Gemini
        analysis = await _generate_final_analysis(session, per_kpi_scores, overall_score)
        
        # Create report
        report = FinalReport(
            session_id=session_id,
            overall_score=overall_score,
            per_kpi_scores=per_kpi_scores,
            strengths=analysis["strengths"],
            weaknesses=analysis["weaknesses"],
            recommendation=analysis["recommendation"],
            detailed_feedback=analysis["detailed_feedback"],
            total_questions=len(session.question_history)
        )
        
        session.status = InterviewStatus.COMPLETED
        store.update_session(session)
        
        logger.info(f"Interview finalized. Overall score: {overall_score:.2f}")
        return report
        
    except Exception as e:
        logger.error(f"Error finalizing interview: {str(e)}")
        raise


async def _generate_question(
    session: InterviewSession,
    is_first: bool = False
) -> Question:
    """Generate a new interview question based on session state."""
    try:
        gemini = get_gemini_client()
        
        # Prepare context
        jd_summary = f"{session.jd.title} at {session.jd.company or 'the company'}"
        resume_summary = f"{session.resume.name} with {len(session.resume.work_experience)} positions"
        
        # Get coverage of KPIs
        kpi_coverage = {}
        for kpi in session.kpis:
            scores = session.kpi_scores.get(kpi.id, [])
            kpi_coverage[kpi.id] = {
                "name": kpi.name,
                "times_evaluated": len(scores),
                "avg_score": sum(scores) / len(scores) if scores else 0,
                "weight": kpi.weight,
                "description": kpi.description
            }
        
        # Previous Q&A context
        recent_qa = []
        for qa_pair in session.question_history[-3:]:  # Last 3 Q&As
            if qa_pair.answer:
                recent_qa.append({
                    "question": qa_pair.question.text,
                    "answer": qa_pair.answer.text[:200]  # Truncate long answers
                })
        
        context_msg = "This is the first question." if is_first else f"Previous Q&As: {recent_qa}"
        
        user_prompt = f"""Generate the next interview question for this session.

Job: {jd_summary}
Candidate: {resume_summary}

KPIs to evaluate:
{chr(10).join(f"- {kpi.name} (weight: {kpi.weight:.2f}): evaluated {kpi_coverage[kpi.id]['times_evaluated']} times" for kpi in session.kpis)}

{context_msg}

Question count so far: {len(session.question_history)}

Return response in this JSON format:
{{
  "question_text": "The interview question",
  "kpi_ids": ["kpi_1", "kpi_2"],
  "difficulty": "easy|medium|hard",
  "question_type": "technical|behavioral|system_design|situational|culture",
  "context": "Optional context or hint about what you're looking for"
}}

Guidelines:
- Focus on KPIs that have been evaluated fewer times
- Weight more important KPIs (higher weight) more heavily
- Start with easier questions and progress to harder ones
- Build on previous answers when appropriate
- Be specific and clear"""
        
        result = await gemini.chat_with_json_response(
            system_prompt=QUESTION_GENERATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.7
        )
        
        # Create Question object
        question = Question(
            id=f"q_{len(session.question_history) + 1}_{uuid.uuid4().hex[:8]}",
            text=result["question_text"],
            kpi_ids=result.get("kpi_ids", []),
            difficulty=Difficulty(result.get("difficulty", "medium")),
            question_type=QuestionType(result.get("question_type", "technical")),
            context=result.get("context")
        )
        
        logger.info(f"Generated question: {question.id} (type: {question.question_type}, difficulty: {question.difficulty})")
        return question
        
    except Exception as e:
        logger.error(f"Error generating question: {str(e)}")
        # Fallback question
        return Question(
            id=f"q_fallback_{uuid.uuid4().hex[:8]}",
            text="Can you tell me about a challenging project you've worked on and how you approached it?",
            kpi_ids=[session.kpis[0].id] if session.kpis else [],
            difficulty=Difficulty.MEDIUM,
            question_type=QuestionType.BEHAVIORAL
        )


async def _evaluate_answer(
    session: InterviewSession,
    question: Question,
    answer: Answer
) -> List[KPIEval]:
    """Evaluate a candidate's answer against relevant KPIs."""
    try:
        gemini = get_gemini_client()
        
        # Get KPIs for this question
        relevant_kpis = [kpi for kpi in session.kpis if kpi.id in question.kpi_ids]
        
        if not relevant_kpis:
            logger.warning(f"No relevant KPIs for question {question.id}")
            return []
        
        kpis_info = "\n".join([
            f"- {kpi.name} (ID: {kpi.id}): {kpi.description} [Expected: {kpi.expected_level}]"
            for kpi in relevant_kpis
        ])
        
        user_prompt = f"""Evaluate this interview answer against the specified KPIs.

Question: {question.text}
Question Type: {question.question_type}
Difficulty: {question.difficulty}

Answer: {answer.text}

KPIs to evaluate:
{kpis_info}

Candidate Background:
- Name: {session.resume.name}
- Experience: {len(session.resume.work_experience)} positions
- Key Skills: {', '.join(session.resume.skills[:5])}

Return evaluation in this JSON format:
{{
  "evaluations": [
    {{
      "kpi_id": "kpi_id",
      "score": 3.5,
      "justification": "Detailed explanation of the score"
    }}
  ],
  "overall_feedback": "Brief overall assessment of the answer"
}}

Scoring guide (0-5):
- 0-1: Poor/Incorrect
- 1-2: Below expectations
- 2-3: Meets basic expectations
- 3-4: Exceeds expectations
- 4-5: Exceptional"""
        
        result = await gemini.chat_with_json_response(
            system_prompt=ANSWER_EVALUATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3  # Lower temperature for consistent scoring
        )
        
        # Create KPIEval objects
        evaluations = [
            KPIEval(
                kpi_id=eval_data["kpi_id"],
                score=min(5.0, max(0.0, float(eval_data["score"]))),  # Clamp to 0-5
                justification=eval_data["justification"]
            )
            for eval_data in result.get("evaluations", [])
        ]
        
        logger.info(f"Evaluated answer for question {question.id}: {len(evaluations)} KPI scores")
        return evaluations
        
    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        # Return neutral score as fallback
        return [
            KPIEval(
                kpi_id=kpi.id,
                score=2.5,
                justification="Automatic neutral score due to evaluation error"
            )
            for kpi in relevant_kpis
        ]


def _should_ask_more_questions(session: InterviewSession) -> bool:
    """Determine if more questions should be asked."""
    settings = get_settings()
    
    # Check minimum questions
    if len(session.question_history) < settings.min_questions_per_interview:
        return True
    
    # Check if all KPIs have been adequately covered
    for kpi in session.kpis:
        scores = session.kpi_scores.get(kpi.id, [])
        # High-weight KPIs should be evaluated at least twice
        min_evaluations = 2 if kpi.weight > 0.2 else 1
        if len(scores) < min_evaluations:
            return True
    
    return False


async def _generate_final_analysis(
    session: InterviewSession,
    per_kpi_scores: List[KPIEval],
    overall_score: float
) -> Dict[str, Any]:
    """Generate detailed final analysis using Gemini."""
    try:
        gemini = get_gemini_client()
        
        # Prepare interview summary
        qa_summary = []
        for i, qa_pair in enumerate(session.question_history, 1):
            if qa_pair.answer:
                qa_summary.append({
                    "question": qa_pair.question.text,
                    "answer_preview": qa_pair.answer.text[:150],
                    "scores": [{"kpi": e.kpi_id, "score": e.score} for e in qa_pair.evaluations]
                })
        
        kpi_summary = [
            {
                "name": next((k.name for k in session.kpis if k.id == eval.kpi_id), "Unknown"),
                "score": eval.score,
                "weight": next((k.weight for k in session.kpis if k.id == eval.kpi_id), 0)
            }
            for eval in per_kpi_scores
        ]
        
        user_prompt = f"""Generate a comprehensive final interview assessment.

Job: {session.jd.title}
Candidate: {session.resume.name}
Overall Score: {overall_score:.2f}/5.0
Total Questions: {len(session.question_history)}

KPI Scores:
{chr(10).join(f"- {kpi['name']}: {kpi['score']:.2f}/5.0 (weight: {kpi['weight']:.2f})" for kpi in kpi_summary)}

Interview Summary:
{qa_summary[:5]}  (showing first 5 Q&As)

Return analysis in this JSON format:
{{
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "recommendation": "Clear hiring recommendation (Strong Hire/Hire/Maybe/No Hire) with brief reasoning",
  "detailed_feedback": "Comprehensive paragraph summarizing the interview performance"
}}

Provide actionable, specific feedback based on the actual interview responses."""
        
        result = await gemini.chat_with_json_response(
            system_prompt="You are an expert hiring manager providing final interview assessments.",
            user_prompt=user_prompt,
            temperature=0.5
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating final analysis: {str(e)}")
        # Return basic analysis
        return {
            "strengths": ["Completed the interview"],
            "weaknesses": ["Unable to generate detailed analysis"],
            "recommendation": f"Score: {overall_score:.2f}/5.0",
            "detailed_feedback": f"Overall interview score: {overall_score:.2f}/5.0 based on {len(session.question_history)} questions."
        }
