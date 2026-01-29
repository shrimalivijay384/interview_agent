# Interview Agent - Complete Flow Diagram

## 🎯 Quick Visual Flow

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          INTERVIEW AGENT SYSTEM                          ┃
┃                     AI-Powered Technical Interview Platform              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                              ┌─────────────┐
                              │   START     │
                              │  (Homepage) │
                              └──────┬──────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
            ┌───────▼────────┐              ┌────────▼────────┐
            │  Upload CV     │              │  Select Existing│
            │  (PDF/DOCX/TXT)│              │  CV from List   │
            └───────┬────────┘              └────────┬────────┘
                    │                                 │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  Auto-Parse CV           │
                    │  • Extract text          │
                    │  • Parse profile         │
                    │  • Add to RAG Vector DB  │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  Generate/Enter JD       │
                    │  • Paste manually OR     │
                    │  • AI auto-generate      │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  Click "Start Interview" │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  Create Interview        │
                    │  Session (SQLite)        │
                    │  session_id: xxx         │
                    └────────────┬─────────────┘
                                 │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    INTERVIEW ORCHESTRATOR STAGES                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: GREETING                                                      │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Agent: InfoCollectorAgent                                │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │  🤖 "Hello! Welcome to your interview. How are you       │          │
│  │      today?"                                              │          │
│  │                                                           │          │
│  │  👤 "I'm good, thank you!"                                │          │
│  │                                                           │          │
│  │  Purpose: Initial engagement & rapport building          │          │
│  │  Duration: 1-2 minutes                                   │          │
│  └──────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: INFO_COLLECTION                                               │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Agent: InfoCollectorAgent                                │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │  🤖 "What's your full name?"                              │          │
│  │  👤 "John Doe"                                            │          │
│  │                                                           │          │
│  │  🤖 "What position are you applying for?"                │          │
│  │  👤 "Senior Python Developer"                            │          │
│  │                                                           │          │
│  │  🤖 "How many years of experience do you have?"          │          │
│  │  👤 "7 years in software development"                    │          │
│  │                                                           │          │
│  │  🤖 "What technologies are you most comfortable with?"   │          │
│  │  👤 "Python, FastAPI, React, PostgreSQL, AWS"            │          │
│  │                                                           │          │
│  │  🤖 "What's your location and timezone?"                 │          │
│  │  👤 "Seattle, WA - Pacific timezone"                     │          │
│  │                                                           │          │
│  │  ✓ Data Collected & Cross-checked with CV               │          │
│  │  ✓ Context Enriched                                      │          │
│  │  Duration: 3-5 minutes                                   │          │
│  └──────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: PROFILE_VALIDATION                                            │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Agent: ProfileValidatorAgent                             │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │  🤖 "Could you share your LinkedIn profile URL?"         │          │
│  │  👤 "linkedin.com/in/johndoe"                            │          │
│  │                                                           │          │
│  │  🔍 System validates LinkedIn:                           │          │
│  │     • Profile exists ✓                                   │          │
│  │     • Matches CV data ✓                                  │          │
│  │     • Experience matches ✓                               │          │
│  │     • No red flags ✓                                     │          │
│  │                                                           │          │
│  │  🤖 "Do you have a GitHub/portfolio to share?"           │          │
│  │  👤 "github.com/johndoe"                                 │          │
│  │                                                           │          │
│  │  🔍 System validates GitHub (optional):                  │          │
│  │     • Public repos found ✓                               │          │
│  │     • Technologies match ✓                               │          │
│  │     • Active contributions ✓                             │          │
│  │                                                           │          │
│  │  ✓ Profile Consistency Report Generated                  │          │
│  │  Duration: 2-3 minutes                                   │          │
│  └──────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: PROJECT_ANALYSIS                                              │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Agent: ProjectAnalyzerAgent                              │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │  🔍 System extracts projects from CV:                     │          │
│  │     1. E-commerce Platform (2023-2024)                   │          │
│  │     2. Real-time Analytics Dashboard (2022-2023)         │          │
│  │     3. API Gateway Service (2021-2022)                   │          │
│  │                                                           │          │
│  │  🤖 "Let's discuss your E-commerce Platform. What was    │          │
│  │      your specific role and responsibilities?"           │          │
│  │                                                           │          │
│  │  👤 "I architected the microservices backend using       │          │
│  │      FastAPI and PostgreSQL. Led team of 4 developers."  │          │
│  │                                                           │          │
│  │  🤖 "What were the main technical challenges?"           │          │
│  │  👤 "Handling 10K concurrent users, ensuring sub-200ms   │          │
│  │      response times, managing distributed transactions."  │          │
│  │                                                           │          │
│  │  🤖 "How did you solve the scalability issues?"          │          │
│  │  👤 "Implemented Redis caching, horizontal scaling with  │          │
│  │      k8s, optimized database queries with indexing."     │          │
│  │                                                           │          │
│  │  🤖 "What was the business impact?"                      │          │
│  │  👤 "40% increase in sales, 60% reduction in cart        │          │
│  │      abandonment, 99.9% uptime achieved."                │          │
│  │                                                           │          │
│  │  ✓ Analyzed: Scope, Technologies, Responsibilities       │          │
│  │  ✓ Evaluated: Complexity, Scale, Impact                  │          │
│  │  ✓ Identified: Standout achievements                     │          │
│  │  Duration: 10-15 minutes                                 │          │
│  └──────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 5: KPI_EXTRACTION & TECHNICAL INTERVIEW                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Agent: KPIDeciderService + Interview Agent              │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │  🔍 System analyzes Job Description:                      │          │
│  │     Extracted KPIs:                                       │          │
│  │     1. Delivery Metrics (speed, scale, reliability)      │          │
│  │     2. Quality Metrics (test coverage, code quality)     │          │
│  │     3. Impact Metrics (revenue, users, efficiency)       │          │
│  │     4. Leadership Metrics (mentoring, ownership)         │          │
│  │     5. Innovation Metrics (process improvement)          │          │
│  │                                                           │          │
│  │  🤖 KPI 1 - Delivery Metrics:                            │          │
│  │     "The JD mentions 'high-traffic systems.' Have you    │          │
│  │      worked on systems handling 1M+ requests/day?"       │          │
│  │                                                           │          │
│  │  👤 "Yes, in my e-commerce project we handled 2M daily   │          │
│  │      requests with peak loads of 10K concurrent users."  │          │
│  │                                                           │          │
│  │  🤖 "How did you ensure 99.9% uptime?"                   │          │
│  │  👤 "Implemented circuit breakers, health checks, auto-  │          │
│  │      scaling, and failover mechanisms in Kubernetes."    │          │
│  │                                                           │          │
│  │  ✓ Score: 90/100 (Excellent)                             │          │
│  │  ✓ Justification: Strong experience, proven metrics      │          │
│  │                                                           │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │                                                           │          │
│  │  🤖 KPI 2 - Quality Metrics:                             │          │
│  │     "What's your approach to testing? Can you share      │          │
│  │      your typical test coverage?"                        │          │
│  │                                                           │          │
│  │  👤 "We maintained 85% test coverage with unit tests,    │          │
│  │      integration tests, and E2E tests using pytest."     │          │
│  │                                                           │          │
│  │  🤖 "How do you handle code reviews?"                    │          │
│  │  👤 "All PRs require 2 approvals. We check correctness,  │          │
│  │      performance, security, and maintainability."        │          │
│  │                                                           │          │
│  │  ✓ Score: 80/100 (Good)                                  │          │
│  │  ✓ Justification: Solid practices, good coverage         │          │
│  │                                                           │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │                                                           │          │
│  │  🤖 KPI 3 - Impact Metrics:                              │          │
│  │     "Can you quantify the business impact of your work?" │          │
│  │                                                           │          │
│  │  👤 "E-commerce project: 40% revenue increase, 2M users, │          │
│  │      Analytics dashboard: 50% faster decision-making."   │          │
│  │                                                           │          │
│  │  ✓ Score: 92/100 (Excellent)                             │          │
│  │  ✓ Justification: Clear business metrics, high impact    │          │
│  │                                                           │          │
│  │  ... (continues for all KPIs)                            │          │
│  │                                                           │          │
│  │  Duration: 15-20 minutes                                 │          │
│  └──────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 6: COMPLETION & REPORT GENERATION                                │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │  Agent: Report Generator (Orchestrator)                   │          │
│  │  ─────────────────────────────────────────────────────────│          │
│  │  🤖 "Thank you for your time! We've completed the        │          │
│  │      interview. You'll receive a detailed report."       │          │
│  │                                                           │          │
│  │  📊 System compiles comprehensive report:                │          │
│  │                                                           │          │
│  │  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │          │
│  │  ┃  INTERVIEW ASSESSMENT REPORT                   ┃   │          │
│  │  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫   │          │
│  │  ┃                                                 ┃   │          │
│  │  ┃  Candidate: John Doe                           ┃   │          │
│  │  ┃  Position: Senior Python Developer             ┃   │          │
│  │  ┃  Interview Date: Jan 28, 2026                  ┃   │          │
│  │  ┃  Duration: 45 minutes                          ┃   │          │
│  │  ┃                                                 ┃   │          │
│  │  ┃  ╔════════════════╗                            ┃   │          │
│  │  ┃  ║   OVERALL      ║                            ┃   │          │
│  │  ┃  ║   SCORE: 85    ║                            ┃   │          │
│  │  ┃  ║   ─────────    ║                            ┃   │          │
│  │  ┃  ║     100        ║                            ┃   │          │
│  │  ┃  ╚════════════════╝                            ┃   │          │
│  │  ┃                                                 ┃   │          │
│  │  ┃  ───────────────────────────────────────────   ┃   │          │
│  │  ┃  KPI SCORES:                                   ┃   │          │
│  │  ┃  • Delivery Metrics:    [Excellent] 90/100    ┃   │          │
│  │  ┃  • Quality Metrics:     [Good]      80/100    ┃   │          │
│  │  ┃  • Impact Metrics:      [Excellent] 92/100    ┃   │          │
│  │  ┃  • Leadership:          [Good]      75/100    ┃   │          │
│  │  ┃  • Innovation:          [Good]      78/100    ┃   │          │
│  │  ┃                                                 ┃   │          │
│  │  ┃  ───────────────────────────────────────────   ┃   │          │
│  │  ┃  STRENGTHS:                                    ┃   │          │
│  │  ┃  ✓ Strong scalability experience              ┃   │          │
│  │  ┃  ✓ Proven system design skills                ┃   │          │
│  │  ┃  ✓ Clear business impact metrics              ┃   │          │
│  │  ┃  ✓ Good testing practices                     ┃   │          │
│  │  ┃  ✓ Effective communication                    ┃   │          │
│  │  ┃                                                 ┃   │          │
│  │  ┃  AREAS FOR IMPROVEMENT:                        ┃   │          │
│  │  ┃  ⚠ Limited cloud-native experience            ┃   │          │
│  │  ┃  ⚠ Could expand DevOps knowledge              ┃   │          │
│  │  ┃                                                 ┃   │          │
│  │  ┃  ───────────────────────────────────────────   ┃   │          │
│  │  ┃  RECOMMENDATION:                               ┃   │          │
│  │  ┃  🟢 STRONG YES                                 ┃   │          │
│  │  ┃                                                 ┃   │          │
│  │  ┃  Excellent candidate for Senior Developer     ┃   │          │
│  │  ┃  role. Strong technical skills, proven track  ┃   │          │
│  │  ┃  record of delivering scalable systems with   ┃   │          │
│  │  ┃  clear business impact.                       ┃   │          │
│  │  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │          │
│  │                                                           │          │
│  │  ✓ Stored in SQLite database                             │          │
│  │  ✓ Available via /api/unified-interview/{id}/report     │          │
│  └──────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Navigate to Report    │
                    │  Page (Frontend)       │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Display Styled Report │
                    │  (using Report.css)    │
                    └────────────┬───────────┘
                                 │
                    ┌────────────▼───────────┐
                    │  [ Start New Interview]│
                    │  [ Download Report ]   │
                    └────────────────────────┘
```

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                              │
│                     React + TypeScript + Vite                        │
│                      http://localhost:5173                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │   Home   │   │   CV     │   │Interview │   │  Report  │        │
│  │   Page   │───│  Upload  │───│   Page   │───│   Page   │        │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
│       │              │               │               │              │
│       └──────────────┴───────────────┴───────────────┘              │
│                              │                                       │
│                         API Client                                   │
│                    (axios/fetch calls)                               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────▼───────────────────────────────────────┐
│                          BACKEND LAYER                               │
│                          FastAPI Server                              │
│                      http://localhost:8000                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      API ROUTES                                │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │  /api/cv/*              CV upload & management                │ │
│  │  /api/unified-interview/* Interview orchestration             │ │
│  │  /api/rag/*             RAG vector search                     │ │
│  │  /api/kpi/*             KPI extraction                        │ │
│  │  /api/health            Health check                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                  ORCHESTRATOR LAYER                            │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │           InterviewOrchestrator (Coordinator)                  │ │
│  │  • Manages 6-stage interview flow                             │ │
│  │  • Coordinates all agents                                     │ │
│  │  • Handles state transitions                                  │ │
│  │  • Session management (SQLite)                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    AGENT LAYER                                 │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  ┌─────────────────┐  ┌──────────────────┐                   │ │
│  │  │InfoCollector    │  │ ProfileValidator │                   │ │
│  │  │Agent            │  │ Agent            │                   │ │
│  │  │• Greeting       │  │• LinkedIn check  │                   │ │
│  │  │• Info collection│  │• GitHub check    │                   │ │
│  │  └─────────────────┘  └──────────────────┘                   │ │
│  │                                                                │ │
│  │  ┌─────────────────┐  ┌──────────────────┐                   │ │
│  │  │ProjectAnalyzer  │  │ KPIDecider       │                   │ │
│  │  │Agent            │  │ Service          │                   │ │
│  │  │• Extract projects│  │• Parse JD       │                   │ │
│  │  │• Deep analysis  │  │• Generate Qs    │                   │ │
│  │  └─────────────────┘  └──────────────────┘                   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   SERVICE LAYER                                │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │ │
│  │  │ RAG System   │  │Resume Parser │  │JD Generator  │       │ │
│  │  │• ChromaDB    │  │• PDF/DOCX    │  │• AI-powered  │       │ │
│  │  │• Vector      │  │• Text extract│  │• CV-based    │       │ │
│  │  │  search      │  └──────────────┘  └──────────────┘       │ │
│  │  └──────────────┘                                             │ │
│  │                                                                │ │
│  │  ┌──────────────┐  ┌──────────────┐                          │ │
│  │  │Gemini Client │  │Serper API    │                          │ │
│  │  │• LLM calls   │  │• Web research│                          │ │
│  │  │• Q generation│  │• Profile check│                         │ │
│  │  └──────────────┘  └──────────────┘                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   DATA LAYER                                   │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │ │
│  │  │  SQLite DB   │  │  ChromaDB    │  │  File System │       │ │
│  │  │• Sessions    │  │• Embeddings  │  │• CV files    │       │ │
│  │  │• Stages      │  │• Candidates  │  │• JSON data   │       │ │
│  │  │• History     │  │• Questions   │  └──────────────┘       │ │
│  │  └──────────────┘  │• Context     │                          │ │
│  │                    └──────────────┘                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW                                  │
└─────────────────────────────────────────────────────────────────────┘

USER INPUT                  PROCESSING                    OUTPUT
───────────                ────────────                  ────────

  CV File                       │
    │                           │
    ├──► Parse PDF/DOCX ────────┤
    │                           │
    └──► Extract Text ──────────┤
                                │
                                ▼
                         ┌──────────────┐
                         │ Resume Parser│
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            ┌───────────────┐      ┌──────────────┐
            │ Profile Data  │      │ RAG Vector   │
            │ (Name, Email) │      │ Database     │
            └───────────────┘      └──────────────┘
                    │                       │
                    │                       │
Job Description     │                       │
    │               │                       │
    ├──► Parse JD ──┴──► KPI Extractor     │
    │                           │           │
    │                           ▼           │
    │                    ┌──────────────┐   │
    │                    │ 5-8 KPIs     │   │
    │                    │ Generated    │   │
    │                    └──────┬───────┘   │
    │                           │           │
    │                           │           │
User Responses                  │           │
    │                           │           │
    ├──► Gemini AI ◄────────────┤           │
    │         │                             │
    │         ├──► Generate Questions       │
    │         │                             │
    │         ├──► Evaluate Answers         │
    │         │                             │
    │         ├──► RAG Search ◄─────────────┘
    │         │    (similar CVs,
    │         │     questions,
    │         │     context)
    │         │
    │         ▼
    │  ┌──────────────┐
    │  │ Interview    │
    │  │ Transcript   │
    │  └──────┬───────┘
    │         │
    │         ▼
    │  ┌──────────────┐
    │  │ Report       │
    │  │ Generator    │
    │  └──────┬───────┘
    │         │
    │         ▼
    │  ┌──────────────┐
    │  │ Final Report │────► Display to User
    │  │ • Score      │
    │  │ • KPI scores │
    │  │ • Strengths  │
    │  │ • Recommend  │
    │  └──────────────┘
```

---

## 📊 State Transition Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INTERVIEW STATE MACHINE                          │
└─────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  IDLE   │ (No active interview)
    └────┬────┘
         │ POST /start
         │
         ▼
    ┌─────────┐
    │GREETING │ Stage 1: Welcome message
    └────┬────┘
         │ user responds
         │
         ▼
    ┌──────────────┐
    │INFO_COLLECT  │ Stage 2: Collect basic info
    └──────┬───────┘
           │ info collected
           │
           ▼
    ┌──────────────┐
    │PROFILE_VALID │ Stage 3: Validate LinkedIn/GitHub
    └──────┬───────┘
           │ validation complete
           │
           ▼
    ┌──────────────┐
    │PROJECT_ANALY │ Stage 4: Analyze projects
    └──────┬───────┘
           │ analysis done
           │
           ▼
    ┌──────────────┐
    │KPI_EXTRACT   │ Stage 5: KPI-based Q&A
    └──────┬───────┘
           │ interview complete
           │
           ▼
    ┌──────────────┐
    │ COMPLETION   │ Stage 6: Generate report
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  COMPLETED   │ (Report available)
    └──────────────┘

Each transition triggered by:
• User response (POST /action)
• Agent completion signal
• Timeout (optional)
```

---

## 🎯 Quick Reference

### Key URLs
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Main API Endpoints
```
POST   /api/cv/upload                     Upload CV
GET    /api/cv/list                       List CVs
POST   /api/cv/{id}/generate-jd           Generate JD

POST   /api/unified-interview/start       Start interview
POST   /api/unified-interview/{id}/action Send response
GET    /api/unified-interview/{id}/status Get stage
GET    /api/unified-interview/{id}/report Get report

GET    /api/rag/stats                     RAG stats
POST   /api/rag/candidates/search         Search CVs
POST   /api/rag/questions/search          Get questions
```

### Interview Duration
- **Total:** ~35-50 minutes
- Stage 1 (Greeting): 1-2 min
- Stage 2 (Info Collection): 3-5 min
- Stage 3 (Profile Validation): 2-3 min
- Stage 4 (Project Analysis): 10-15 min
- Stage 5 (KPI Interview): 15-20 min
- Stage 6 (Completion): 1-2 min

### Technologies Used
- **Frontend:** React, TypeScript, Vite
- **Backend:** FastAPI, Python 3.10+
- **LLM:** Google Gemini 2.5 Flash Lite
- **Vector DB:** ChromaDB
- **Embeddings:** SentenceTransformer (all-MiniLM-L6-v2)
- **Database:** SQLite
- **Web Search:** Serper API

---

## 🚀 Quick Start

```bash
# 1. Start Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Start Frontend
cd frontend
npm run dev

# 3. Open Browser
http://localhost:5173

# 4. Upload CV → Start Interview → View Report
```

---

**Last Updated:** January 28, 2026  
**Version:** 1.0.0  
**Status:** ✅ Fully Operational
