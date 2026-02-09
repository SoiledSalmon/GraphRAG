# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Backend Module

This is the FastAPI backend for GraphRAG. Run from the **project root**, not this directory:

```bash
# From project root
uvicorn backend.main:app --reload
```

## Module Structure

```
main.py              # FastAPI app, routes /health and /chat
├── rag/
│   ├── extractor.py     # spaCy NER + keyword topic detection (USED)
│   ├── baseline.py      # In-memory deque storage (USED)
│   ├── prompt_builder.py # Graph context → LLM prompt (USED)
│   └── pipeline.py      # UNUSED stubs - do not modify
├── graph/
│   ├── graph.py         # GraphMemory: Neo4j write operations
│   └── retriever.py     # GraphRetriever: Neo4j read operations
└── llm/
    └── gemini_client.py # Gemini API client (never throws)
```

## Request Flow

**POST /chat** dispatches based on `mode` field:

| Mode | Context Source | Storage | Prompt Builder |
|------|---------------|---------|----------------|
| `baseline` | `baseline.py` deque (last 5 msgs) | In-memory | Manual concat in main.py |
| `graph` | `retriever.py` Neo4j query | Neo4j persist | `prompt_builder.py` |

## Critical Implementation Details

- **Graph mode ordering**: Retrieves context BEFORE writing the current interaction (prevents self-reference)
- **Gemini client**: All exceptions caught - returns `"The system is temporarily unavailable."` on any failure
- **spaCy loading**: `extractor.py` loads model at import time (`nlp = spacy.load(...)`)
- **Baseline memory**: Unbounded user dictionary with bounded per-user deque - memory leak potential with many unique users
- **pipeline.py**: Contains unused stub functions - the actual implementations are in separate modules

## Environment Variables (loaded in main.py)

```
GEMINI_API_KEY    # Required
NEO4J_URI         # Default: bolt://localhost:7687
NEO4J_USERNAME    # Default: neo4j
NEO4J_PASSWORD    # Default: password
```
