/**
 * Report page - final interview assessment
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';
import apiClient from '../api/client';
import '../styles/Report.css';

const Report: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId, finalReport, setFinalReport, resetInterview, kpis } =
    useInterview();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      navigate('/');
      return;
    }

    if (!finalReport) {
      generateReport();
    }
  }, [sessionId, finalReport]);

  const generateReport = async () => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.endInterview({
        session_id: sessionId,
      });
      setFinalReport(response.report);
    } catch (err: any) {
      console.error('Error generating report:', err);
      setError(
        err.response?.data?.detail || 'Failed to generate report. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStartNew = () => {
    resetInterview();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="report-container">
        <div className="loading-info">
          <h2>⏳ Generating Your Report...</h2>
          <p>Analyzing your responses and preparing comprehensive feedback</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="report-container">
        <div className="error-message">{error}</div>
        <button onClick={handleStartNew}>Start New Interview</button>
      </div>
    );
  }

  if (!finalReport) {
    return <div className="loading">Loading report...</div>;
  }

  const getScoreColor = (score: number) => {
    if (score >= 4) return 'score-excellent';
    if (score >= 3) return 'score-good';
    if (score >= 2) return 'score-fair';
    return 'score-poor';
  };

  const getKPIName = (kpiId: string) => {
    const kpi = kpis.find((k) => k.id === kpiId);
    return kpi?.name || kpiId;
  };

  return (
    <div className="report-container">
      <div className="report-header">
        <h1>🎉 Interview Complete!</h1>
        <p>Here's your comprehensive assessment</p>
      </div>

      <div className="overall-score">
        <h2>Overall Score</h2>
        <div className={`score-circle ${getScoreColor(finalReport.overall_score)}`}>
          <span className="score-value">{finalReport.overall_score.toFixed(1)}</span>
          <span className="score-max">/5.0</span>
        </div>
        <p className="recommendation">{finalReport.recommendation}</p>
      </div>

      <div className="report-section">
        <h2>📊 Performance by Criteria</h2>
        <div className="kpi-scores">
          {finalReport.per_kpi_scores.map((kpiScore) => (
            <div key={kpiScore.kpi_id} className="kpi-score-card">
              <div className="kpi-score-header">
                <h3>{getKPIName(kpiScore.kpi_id)}</h3>
                <span className={`score-badge ${getScoreColor(kpiScore.score)}`}>
                  {kpiScore.score.toFixed(1)}/5.0
                </span>
              </div>
              <p className="kpi-justification">{kpiScore.justification}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="report-section">
        <h2>💪 Strengths</h2>
        <ul className="feedback-list strengths-list">
          {finalReport.strengths.map((strength, index) => (
            <li key={index}>{strength}</li>
          ))}
        </ul>
      </div>

      <div className="report-section">
        <h2>📈 Areas for Improvement</h2>
        <ul className="feedback-list weaknesses-list">
          {finalReport.weaknesses.map((weakness, index) => (
            <li key={index}>{weakness}</li>
          ))}
        </ul>
      </div>

      {finalReport.detailed_feedback && (
        <div className="report-section">
          <h2>📝 Detailed Feedback</h2>
          <p className="detailed-feedback">{finalReport.detailed_feedback}</p>
        </div>
      )}

      <div className="report-footer">
        <p className="interview-stats">
          Total Questions Answered: {finalReport.total_questions}
        </p>
        <button className="start-new-button" onClick={handleStartNew}>
          Start New Interview
        </button>
      </div>
    </div>
  );
};

export default Report;
