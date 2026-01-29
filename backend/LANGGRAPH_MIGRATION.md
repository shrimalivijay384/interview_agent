# LangGraph Migration Guide for Interview Agent

## Overview

This guide walks you through migrating the current Interview Agent from a custom orchestrator to **LangGraph** - a library for building stateful, multi-actor applications with LLMs.

## Why LangGraph?

✅ **Built-in State Management** - Automatic state persistence and checkpointing  
✅ **Visual Graph Representation** - See your workflow visually  
✅ **Conditional Edges** - Dynamic routing based on agent outputs  
✅ **Human-in-the-loop** - Easy pause/resume for user input  
✅ **Parallel Execution** - Run multiple agents concurrently  
✅ **Time Travel** - Replay and debug interview flows  
✅ **Built on LangChain** - Seamless integration with existing tools  

## Current vs LangGraph Architecture

### Current Architecture:
```
InterviewOrchestrator
├── Stage-based state machine
├── Manual state transitions
├── Sequential agent calls
└── Custom session management
```

### LangGraph Architecture:
```
StateGraph
├── Node-based workflow
├── Automatic state updates
├── Conditional routing
├── Built-in checkpointing
└── Graph visualization
```

---

## Installation

```bash
cd backend
pip install langgraph langchain-google-genai langsmith
```

---

## Implementation Plan

### Phase 1: Core Setup
1. Define Interview State Schema
2. Create Graph Structure
3. Migrate Agents to Nodes

### Phase 2: Graph Construction
4. Add Conditional Edges
5. Implement Human-in-the-loop
6. Add Checkpointing

### Phase 3: Integration
7. Update API Routes
8. Migrate Database Layer
9. Testing & Validation

---

## File Structure

```
backend/
├── app/
│   ├── langgraph/
│   │   ├── __init__.py
│   │   ├── graph.py                 # Main graph definition
│   │   ├── state.py                 # State schema
│   │   ├── nodes.py                 # Agent nodes
│   │   ├── edges.py                 # Conditional edges
│   │   └── checkpoints.py           # State persistence
│   ├── agents/                      # Refactored agents
│   │   ├── __init__.py
│   │   ├── info_collector.py
│   │   ├── profile_validator.py
│   │   ├── project_analyzer.py
│   │   └── kpi_interviewer.py
│   ├── routes/
│   │   └── langgraph_interview.py  # New LangGraph routes
│   └── services/                    # Existing services
```

---

## Next Steps

Run the following command to start the migration:

```bash
# Install dependencies
cd backend
pip install langgraph langchain-google-genai langsmith

# The implementation files will be created in the following order:
# 1. app/langgraph/state.py
# 2. app/agents/*.py (refactored)
# 3. app/langgraph/nodes.py
# 4. app/langgraph/edges.py
# 5. app/langgraph/graph.py
# 6. app/routes/langgraph_interview.py
```

Let's proceed with the implementation!
