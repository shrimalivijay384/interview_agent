import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { InterviewProvider } from './context/InterviewContext';
import Home from './pages/Home';
import Interview from './pages/Interview';
import Report from './pages/Report';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <InterviewProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/interview" element={<Interview />} />
          <Route path="/report" element={<Report />} />
        </Routes>
      </InterviewProvider>
    </BrowserRouter>
  </React.StrictMode>
);
