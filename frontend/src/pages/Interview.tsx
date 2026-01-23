/**
 * Interview page - main interview screen
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';
import apiClient from '../api/client';
import '../styles/Interview.css';

const Interview: React.FC = () => {
  const navigate = useNavigate();
  const {
    sessionId,
    currentQuestion,
    setCurrentQuestion,
    kpis,
    questionHistory,
    addQuestionToHistory,
    setIsComplete,
  } = useInterview();

  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [progress, setProgress] = useState<any>(null);

  useEffect(() => {
    if (!sessionId || !currentQuestion) {
      navigate('/');
    }
    setStartTime(Date.now());
  }, [sessionId, currentQuestion, navigate]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || !sessionId) return;

    setLoading(true);
    setError(null);

    const duration = (Date.now() - startTime) / 1000;

    try {
      const response = await apiClient.submitAnswer({
        session_id: sessionId,
        answer_text: answer,
        duration_seconds: duration,
      });

      setProgress(response.progress);

      if (response.is_complete) {
        setIsComplete(true);
        navigate('/report');
      } else if (response.next_question) {
        setCurrentQuestion(response.next_question);
        addQuestionToHistory(response.next_question);
        setAnswer('');
        setStartTime(Date.now());
      }
    } catch (err: any) {
      console.error('Error submitting answer:', err);
      setError(
        err.response?.data?.detail || 'Failed to submit answer. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleEndInterview = () => {
    if (window.confirm('Are you sure you want to end the interview early?')) {
      navigate('/report');
    }
  };

  if (!currentQuestion) {
    return <div className="loading">Loading...</div>;
  }

  const questionNumber = questionHistory.length;

  return (
    <div className="interview-container">
      <div className="interview-header">
        <h2>Interview in Progress</h2>
        <button className="end-button" onClick={handleEndInterview}>
          End Interview
        </button>
      </div>

      <div className="progress-bar-container">
        <div className="progress-info">
          <span>Question {questionNumber}</span>
          {progress && (
            <span>{progress.total_questions} questions asked</span>
          )}
        </div>
      </div>

      <div className="kpi-overview">
        <h3>Evaluation Criteria:</h3>
        <div className="kpi-list">
          {kpis.map((kpi) => (
            <div key={kpi.id} className="kpi-item">
              <span className="kpi-name">{kpi.name}</span>
              <span className="kpi-weight">{(kpi.weight * 100).toFixed(0)}%</span>
              {progress?.kpi_coverage?.[kpi.name] && (
                <span className="kpi-score">
                  Avg: {progress.kpi_coverage[kpi.name].avg_score.toFixed(1)}/5.0
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="question-section">
        <div className="question-header">
          <span className="question-type">{currentQuestion.question_type}</span>
          <span className="question-difficulty">{currentQuestion.difficulty}</span>
        </div>
        <h3>Question:</h3>
        <p className="question-text">{currentQuestion.text}</p>
        {currentQuestion.context && (
          <p className="question-context">
            <em>{currentQuestion.context}</em>
          </p>
        )}
      </div>

      <div className="answer-section">
        <label htmlFor="answer">Your Answer:</label>
        <textarea
          id="answer"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Type your answer here..."
          rows={10}
          disabled={loading}
        />
        <div className="answer-actions">
          <button
            className="submit-button"
            onClick={handleSubmitAnswer}
            disabled={loading || !answer.trim()}
          >
            {loading ? 'Submitting...' : 'Submit Answer'}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading && (
        <div className="loading-info">
          <p>⏳ Evaluating your answer and generating next question...</p>
        </div>
      )}
    </div>
  );
};

export default Interview;
