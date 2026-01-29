/**
 * API client for Interview Agent backend
 */
import axios, { AxiosInstance } from 'axios';
import {
  StartInterviewRequest,
  StartInterviewResponse,
  SubmitAnswerRequest,
  SubmitAnswerResponse,
  EndInterviewRequest,
  EndInterviewResponse,
} from '../types/api';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 seconds for LLM operations
    });
  }

  /**
   * Start a new interview session
   */
  async startInterview(
    request: StartInterviewRequest
  ): Promise<StartInterviewResponse> {
    const response = await this.client.post<StartInterviewResponse>(
      '/api/interview/start',
      request
    );
    return response.data;
  }

  /**
   * Submit an answer and get next question
   */
  async submitAnswer(
    request: SubmitAnswerRequest
  ): Promise<SubmitAnswerResponse> {
    const response = await this.client.post<SubmitAnswerResponse>(
      '/api/interview/answer',
      request
    );
    return response.data;
  }

  /**
   * End interview and get final report
   */
  async endInterview(
    request: EndInterviewRequest
  ): Promise<EndInterviewResponse> {
    const response = await this.client.post<EndInterviewResponse>(
      '/api/interview/end',
      request
    );
    return response.data;
  }

  /**
   * Get session information
   */
  async getSessionInfo(sessionId: string): Promise<any> {
    const response = await this.client.get(
      `/api/interview/session/${sessionId}`
    );
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * List all uploaded CVs
   */
  async listUploadedCVs(): Promise<any> {
    const response = await this.client.get('/api/cv/list');
    return response.data;
  }

  /**
   * Get CV by ID
   */
  async getCVById(cvId: string): Promise<any> {
    const response = await this.client.get(`/api/cv/${cvId}`);
    return response.data;
  }

  /**
   * Upload CV file
   */
  async uploadCVFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/cv/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Upload CV as text
   */
  async uploadCVText(cvText: string): Promise<any> {
    const formData = new FormData();
    formData.append('cv_text', cvText);

    const response = await this.client.post('/api/cv/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Generate JD based on CV
   */
  async generateJDForCV(cvId: string): Promise<any> {
    const response = await this.client.post(`/api/cv/${cvId}/generate-jd`);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
