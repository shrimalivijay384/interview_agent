/**
 * Home page - JD and Resume upload
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';
import apiClient from '../api/client';
import '../styles/Home.css';

type UploadMode = 'text' | 'file' | 'select';

interface UploadedCV {
  cv_id: string;
  name: string;
  email: string;
  uploaded_at: string;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { setSessionId, setCurrentQuestion, setKpis, addQuestionToHistory } =
    useInterview();

  const [jdText, setJdText] = useState('');
  const [cvText, setCvText] = useState('');
  const [uploadMode, setUploadMode] = useState<UploadMode>('text');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedCVs, setUploadedCVs] = useState<UploadedCV[]>([]);
  const [selectedCVId, setSelectedCVId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [autoStart, setAutoStart] = useState(false);

  // Load uploaded CVs on component mount
  useEffect(() => {
    loadUploadedCVs();
  }, []);

  const loadUploadedCVs = async () => {
    try {
      const response = await apiClient.listUploadedCVs();
      if (response.success && response.cvs) {
        setUploadedCVs(response.cvs);
      }
    } catch (err) {
      console.error('Error loading CVs:', err);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = ['.pdf', '.docx', '.doc', '.txt'];
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validTypes.includes(fileExt)) {
        setError('Please upload a valid file format: PDF, DOCX, DOC, or TXT');
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUploadFile = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setUploadProgress('Uploading file...');
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8000/api/cv/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setUploadProgress('File uploaded successfully! ✓');
      
      // Set CV text from parsed data
      if (data.parsed_data && data.parsed_data.raw_text) {
        setCvText(data.parsed_data.raw_text);
      }

      // Reload CV list
      await loadUploadedCVs();
      
      setTimeout(() => {
        setUploadProgress('');
      }, 2000);

    } catch (err: any) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCV = async (cvId: string) => {
    if (!cvId) {
      setCvText('');
      setJdText('');
      setSelectedCVId('');
      return;
    }

    setLoading(true);
    setUploadProgress('Loading CV...');
    setError(null);

    try {
      // Load CV data
      const cvResponse = await apiClient.getCVById(cvId);
      if (cvResponse.success && cvResponse.data) {
        // Use raw_text if available, otherwise construct from parsed_data
        const cvData = cvResponse.data;
        const text = cvData.raw_text || JSON.stringify(cvData, null, 2);
        setCvText(text);
        setSelectedCVId(cvId);
        setUploadProgress('CV loaded! Generating matching job description...');
        
        // Automatically generate JD for this CV
        try {
          const jdResponse = await apiClient.generateJDForCV(cvId);
          if (jdResponse.success && jdResponse.jd_text) {
            setJdText(jdResponse.jd_text);
            setUploadProgress('✓ CV and Job Description ready!');
            
            // If auto-start is enabled, start interview automatically
            if (autoStart && text && jdResponse.jd_text) {
              setUploadProgress('Starting interview automatically...');
              setTimeout(() => {
                startInterviewWithData(jdResponse.jd_text, text);
              }, 1000);
            } else {
              // Clear progress message after 2 seconds
              setTimeout(() => {
                setUploadProgress('');
              }, 2000);
            }
          }
        } catch (jdErr) {
          console.error('Error generating JD:', jdErr);
          setUploadProgress('✓ CV loaded! Please enter job description manually.');
          setTimeout(() => {
            setUploadProgress('');
          }, 3000);
        }
      }
    } catch (err) {
      console.error('Error loading CV:', err);
      setError('Failed to load selected CV');
      setUploadProgress('');
    } finally {
      if (!autoStart) {
        setLoading(false);
      }
    }
  };

  const startInterviewWithData = async (jd: string, cv: string) => {
    try {
      const response = await apiClient.startInterview({
        jd_text: jd,
        cv_text: cv,
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
      setLoading(false);
    }
  };

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
            <label>Resume / CV</label>
            
            {/* Upload Mode Selector */}
            <div className="upload-mode-selector">
              <button
                type="button"
                className={`mode-btn ${uploadMode === 'text' ? 'active' : ''}`}
                onClick={() => setUploadMode('text')}
                disabled={loading}
              >
                📝 Paste Text
              </button>
              <button
                type="button"
                className={`mode-btn ${uploadMode === 'file' ? 'active' : ''}`}
                onClick={() => setUploadMode('file')}
                disabled={loading}
              >
                📁 Upload File
              </button>
              <button
                type="button"
                className={`mode-btn ${uploadMode === 'select' ? 'active' : ''}`}
                onClick={() => setUploadMode('select')}
                disabled={loading}
              >
                📋 Select Uploaded
              </button>
            </div>

            {/* Text Input Mode */}
            {uploadMode === 'text' && (
              <textarea
                id="cv"
                value={cvText}
                onChange={(e) => setCvText(e.target.value)}
                placeholder="Paste your resume/CV here..."
                rows={8}
                disabled={loading}
              />
            )}

            {/* File Upload Mode */}
            {uploadMode === 'file' && (
              <div className="file-upload-section">
                <input
                  type="file"
                  id="cv-file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={handleFileSelect}
                  disabled={loading}
                  className="file-input"
                />
                <label htmlFor="cv-file" className="file-input-label">
                  {selectedFile ? (
                    <span>📄 {selectedFile.name}</span>
                  ) : (
                    <span>📁 Choose file (PDF, DOCX, DOC, TXT)</span>
                  )}
                </label>
                {selectedFile && (
                  <button
                    type="button"
                    className="upload-btn"
                    onClick={handleUploadFile}
                    disabled={loading}
                  >
                    ⬆️ Upload & Parse
                  </button>
                )}
                {uploadProgress && (
                  <div className="upload-progress">{uploadProgress}</div>
                )}
              </div>
            )}

            {/* Select Uploaded CV Mode */}
            {uploadMode === 'select' && (
              <div className="select-cv-section">
                <div className="auto-start-toggle">
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={autoStart}
                      onChange={(e) => setAutoStart(e.target.checked)}
                      disabled={loading}
                    />
                    <span className="toggle-text">
                      🚀 Auto-start interview after selecting CV
                    </span>
                  </label>
                  <p className="toggle-hint">
                    When enabled, the interview will start automatically after generating the job description.
                  </p>
                </div>
                
                <select
                  value={selectedCVId}
                  onChange={(e) => handleSelectCV(e.target.value)}
                  disabled={loading}
                  className="cv-select"
                >
                  <option value="">-- Select a CV --</option>
                  {uploadedCVs.map((cv) => (
                    <option key={cv.cv_id} value={cv.cv_id}>
                      {cv.name} ({cv.email}) - {new Date(cv.uploaded_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
                {uploadedCVs.length === 0 && (
                  <p className="no-cvs-message">
                    No CVs uploaded yet. Upload one using the "Upload File" option.
                  </p>
                )}
              </div>
            )}

            {/* Show CV text preview if in select mode */}
            {uploadMode === 'select' && cvText && (
              <textarea
                value={cvText}
                readOnly
                rows={6}
                className="cv-preview"
                placeholder="Selected CV will appear here..."
              />
            )}
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
