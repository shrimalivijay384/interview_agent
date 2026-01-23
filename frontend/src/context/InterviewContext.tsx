/**
 * Interview Context - manages global interview state
 */
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Question, KPI, FinalReport } from '../types/api';

interface InterviewContextType {
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
  currentQuestion: Question | null;
  setCurrentQuestion: (question: Question | null) => void;
  kpis: KPI[];
  setKpis: (kpis: KPI[]) => void;
  questionHistory: Question[];
  addQuestionToHistory: (question: Question) => void;
  isComplete: boolean;
  setIsComplete: (complete: boolean) => void;
  finalReport: FinalReport | null;
  setFinalReport: (report: FinalReport | null) => void;
  resetInterview: () => void;
}

const InterviewContext = createContext<InterviewContextType | undefined>(
  undefined
);

export const useInterview = () => {
  const context = useContext(InterviewContext);
  if (!context) {
    throw new Error('useInterview must be used within InterviewProvider');
  }
  return context;
};

interface InterviewProviderProps {
  children: ReactNode;
}

export const InterviewProvider: React.FC<InterviewProviderProps> = ({
  children,
}) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [questionHistory, setQuestionHistory] = useState<Question[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [finalReport, setFinalReport] = useState<FinalReport | null>(null);

  const addQuestionToHistory = (question: Question) => {
    setQuestionHistory((prev) => [...prev, question]);
  };

  const resetInterview = () => {
    setSessionId(null);
    setCurrentQuestion(null);
    setKpis([]);
    setQuestionHistory([]);
    setIsComplete(false);
    setFinalReport(null);
  };

  return (
    <InterviewContext.Provider
      value={{
        sessionId,
        setSessionId,
        currentQuestion,
        setCurrentQuestion,
        kpis,
        setKpis,
        questionHistory,
        addQuestionToHistory,
        isComplete,
        setIsComplete,
        finalReport,
        setFinalReport,
        resetInterview,
      }}
    >
      {children}
    </InterviewContext.Provider>
  );
};
