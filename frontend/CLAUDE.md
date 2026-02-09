# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Frontend Module

Streamlit chat UI for GraphRAG. Single file application.

```bash
# Run from project root
streamlit run frontend/ui.py
```

Opens at http://localhost:8501

## Backend Dependency

Requires backend running at http://localhost:8000. The frontend calls `POST /chat` with:
```json
{"user_id": "demo_user", "message": "...", "mode": "baseline"|"graph"}
```

**Note**: `user_id` is hardcoded to `"demo_user"` - all sessions share the same graph memory.

## UI Structure

- **Sidebar**: Mode toggle between "Baseline RAG" and "Graph-RAG"
- **Main area**: Chat interface with session-based message history (`st.session_state.messages`)
- **Styling**: Custom CSS with dark gradient background (lines 16-50)

## Streamlit Constraint

`st.set_page_config()` must be the first Streamlit command (line 8). Do not add any `st.*` calls before it.
