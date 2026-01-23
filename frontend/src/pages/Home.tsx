/**
 * Home page - JD and Resume upload
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';
import apiClient from '../api/client';
import '../styles/Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { setSessionId, setCurrentQuestion, setKpis, addQuestionToHistory } =
    useInterview();

  const [jdText, setJdText] = useState('');
  const [cvText, setCvText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartInterview = async () => {
    if (!jdText.trim() || !cvText.trim()) {
      setError('Please provide both Job Description and Resume/CV');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.startInterview({
        jd_text: jdText,
        cv_text: cvText,
      });

      setSessionId(response.session_id);
      setCurrentQuestion(response.first_question);
      setKpis(response.kpis);
      addQuestionToHistory(response.first_question);

      navigate('/interview');
    } catch (err: any) {
      console.error('Error starting interview:', err);
      setError(
        err.response?.data?.detail || 'Failed to start interview. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="home-content">
        <h1>🎯 AI Interview Agent</h1>
        <p className="subtitle">
          Intelligent interview system powered by Google Gemini
        </p>

        <div className="info-box">
          <h3>How it works:</h3>
          <ol>
            <li>Provide the Job Description and your Resume/CV</li>
            <li>Our AI analyzes both to determine evaluation criteria (KPIs)</li>
            <li>Answer a series of tailored interview questions</li>
            <li>Receive comprehensive feedback and assessment</li>
          </ol>
        </div>

        <div className="form-section">
          <div className="input-group">
            <label htmlFor="jd">Job Description</label>
            <textarea
              id="jd"
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the job description here..."
              rows={8}
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="cv">Resume / CV</label>
            <textarea
              id="cv"
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              placeholder="Paste your resume/CV here..."
              rows={8}
              disabled={loading}
            />
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          className="start-button"
          onClick={handleStartInterview}
          disabled={loading || !jdText.trim() || !cvText.trim()}
        >
          {loading ? 'Processing...' : 'Start Interview'}
        </button>

        {loading && (
          <div className="loading-info">
            <p>⏳ Analyzing job description and resume...</p>
            <p>This may take 10-20 seconds</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
