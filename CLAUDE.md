# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GraphRAG is a FastAPI backend implementing dual-mode conversational AI: **baseline** (in-memory deque) vs **graph** (Neo4j-persisted knowledge graph). It uses spaCy NER for entity extraction and Google Gemini API for response generation.

## Commands

```bash
# Install dependencies
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start backend (from project root)
uvicorn backend.main:app --reload

# Start frontend (optional)
streamlit run frontend/ui.py

# Verify environment before running
python check_environment.py

# Run validation tests (requires running backend)
python test_validation.py
```

## Required Environment Variables

Create a `.env` file in project root:
```
GEMINI_API_KEY=your_key_here
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

The backend loads `.env` via `python-dotenv` at startup in `main.py`.

## Architecture

```
POST /chat {user_id, message, mode: "graph"|"baseline"}
         │
         ▼
    ┌────────────────────────────────────────────────────┐
    │                  backend/main.py                    │
    │  • Loads .env via load_dotenv()                    │
    │  • Routes to baseline or graph mode                │
    └────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
    BASELINE MODE                  GRAPH MODE
    ├─ rag/baseline.py             ├─ rag/extractor.py (spaCy NER)
    │  └─ deque(maxlen=5)          ├─ graph/retriever.py (Neo4j read)
    │     per user                 ├─ rag/prompt_builder.py
    └─ Manual prompt concat        └─ graph/graph.py (Neo4j write)
         │                              │
         └──────────────┬───────────────┘
                        ▼
              llm/gemini_client.py
              └─ Returns fallback on any failure (defensive)
```

## Key Design Decisions

- **Graph mode flow**: Retrieve context FIRST, then write interaction (prevents self-referential queries)
- **Gemini client**: Never throws - returns `"The system is temporarily unavailable."` on any error
- **spaCy model**: Loaded at module import time in `extractor.py`
- **Neo4j connection**: Uses `neo4j+s://` scheme for TLS (Aura compatible)

## Neo4j Graph Schema

```
(:User {id}) -[:ASKED_ABOUT]-> (:Event {type, timestamp, content})
(:Event) -[:MENTIONS]-> (:Entity {name})
(:Event) -[:ASKED_ABOUT]-> (:Topic {name})
```

Topics are keyword-based: "LLMs", "RAG", "Knowledge Graphs" (see `extractor.py` lines 20-30).
