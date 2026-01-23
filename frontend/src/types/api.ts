/**
 * TypeScript types for the Interview Agent API
 */

export enum ExperienceLevel {
  JUNIOR = 'junior',
  MID = 'mid',
  SENIOR = 'senior',
  EXPERT = 'expert',
}

export enum QuestionType {
  TECHNICAL = 'technical',
  BEHAVIORAL = 'behavioral',
  SYSTEM_DESIGN = 'system_design',
  CULTURE = 'culture',
  SITUATIONAL = 'situational',
}

export enum Difficulty {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

export enum InterviewStatus {
  INITIALIZED = 'initialized',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export interface KPI {
  id: string;
  name: string;
  weight: number;
  description: string;
  expected_level: ExperienceLevel;
  category: string;
}

export interface Question {
  id: string;
  text: string;
  kpi_ids: string[];
  difficulty: Difficulty;
  question_type: QuestionType;
  context?: string;
  follow_up: boolean;
}

export interface KPIEval {
  kpi_id: string;
  score: number;
  justification: string;
  timestamp: string;
}

export interface FinalReport {
  session_id: string;
  overall_score: number;
  per_kpi_scores: KPIEval[];
  strengths: string[];
  weaknesses: string[];
  recommendation: string;
  detailed_feedback?: string;
  total_questions: number;
  timestamp: string;
}

// API Request/Response types

export interface StartInterviewRequest {
  jd_text: string;
  cv_text: string;
}

export interface StartInterviewResponse {
  session_id: string;
  first_question: Question;
  kpis: KPI[];
  message: string;
}

export interface SubmitAnswerRequest {
  session_id: string;
  answer_text: string;
  duration_seconds?: number;
}

export interface SubmitAnswerResponse {
  session_id: string;
  next_question?: Question;
  evaluation_summary?: string;
  is_complete: boolean;
  progress: {
    total_questions: number;
    kpi_coverage: Record<string, { evaluations: number; avg_score: number }>;
  };
}

export interface EndInterviewRequest {
  session_id: string;
}

export interface EndInterviewResponse {
  session_id: string;
  report: FinalReport;
}
