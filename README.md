# GraphRAG

Linked-Memory Graphs Architectures to Enhance Contextual Adaptation in LLM-based Dialogue Systems

## Overview

GraphRAG is a FastAPI backend + Streamlit frontend implementing **dual-mode conversational AI**:

- **Baseline Mode**: In-memory deque storing the last 5 messages per user
- **Graph Mode**: Neo4j-persisted knowledge graph with entity extraction

The system uses spaCy NER for entity extraction and Google Gemini API for response generation.

## Features

- Dual retrieval modes for A/B comparison
- Entity extraction using spaCy NLP
- Knowledge graph persistence with Neo4j
- Defensive error handling throughout
- Real-time mode switching in UI

## Quick Start

### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `GEMINI_API_KEY` - Google Gemini API key
- `NEO4J_URI` - Neo4j connection URI (e.g., `neo4j+s://xxx.databases.neo4j.io`)
- `NEO4J_USERNAME` - Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD` - Neo4j password

### 3. Verify Environment

```bash
python check_environment.py
```

### 4. Start Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs at http://localhost:8000

### 5. Start Frontend (Optional)

```bash
streamlit run frontend/ui.py
```

Frontend runs at http://localhost:8501

## Architecture

```
POST /chat {user_id, message, mode: "graph"|"baseline"}
         |
         v
    +--------------------+
    |   backend/main.py  |
    +--------------------+
         |            |
         v            v
    BASELINE       GRAPH
    (deque)       (Neo4j)
         |            |
         +-----+------+
               v
        Gemini API
```

## API

### POST /chat

```json
{
  "user_id": "string",
  "message": "string",
  "mode": "baseline" | "graph"
}
```

Response:
```json
{
  "response": "string"
}
```

## Modes Explained

### Baseline RAG
- Stores last 5 messages per user in memory
- Simple context concatenation
- No persistence across restarts

### Graph-RAG
- Extracts entities using spaCy NER
- Stores interactions in Neo4j knowledge graph
- Retrieves related context via graph traversal
- Persistent across restarts

## Validation

```bash
# Run validation tests (requires running backend)
python test_validation.py
```

## License

MIT
