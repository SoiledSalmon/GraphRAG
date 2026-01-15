# GraphRAG System - Setup & Validation Guide

## Project Status: VALIDATION PHASE

This is a **validation and testing phase** - NO code refactoring or feature development.
Goal: Verify the system works end-to-end and is ready for demo/submission.

## Critical Fix Applied

✅ **Fixed syntax error in `backend/graph/graph.py`**
- Line 15: Removed extra quote in Cypher query definition
- Module now imports without syntax errors

## Environment Setup

### Prerequisites
- Python 3.8+ (Detected: Python 3.14.0)
- Neo4j Database (running on bolt://localhost:7687)
- Gemini API Key

### Step 1: Install Dependencies

```powershell
# Install all required packages
python -m pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### Step 2: Configure Environment Variables

Create a `.env` file or set environment variables:

**Required:**
```
GEMINI_API_KEY=your_gemini_api_key_here
```

**Optional (with defaults):**
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

**PowerShell example:**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
$env:NEO4J_PASSWORD="your_neo4j_password"
```

### Step 3: Start Neo4j Database

Ensure Neo4j is running and accessible:
```powershell
# If using Docker:
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

# Or start your local Neo4j instance
```

### Step 4: Verify Environment

```powershell
python check_environment.py
```

Expected output: `✓ ENVIRONMENT READY`

## Running the System

### Start Backend Server

```powershell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### Start Frontend (Optional - Separate Terminal)

```powershell
streamlit run frontend/ui.py
```

Frontend will open in browser at: `http://localhost:8501`

## Validation & Testing

### Run Comprehensive Validation Suite

```powershell
python test_validation.py
```

This script tests:
1. ✅ Health endpoint (`/health`)
2. ✅ Baseline mode (text memory)
3. ✅ Graph mode (Neo4j memory)
4. ✅ Behavioral difference between modes
5. ✅ Neo4j database structure

### Expected Test Flow

**Baseline Mode:**
- Q1: "Explain Neo4j" → Response generated
- Q2: "How is it used in Graph RAG?" → Uses last 5 messages as context

**Graph Mode:**
- Q1: "Explain Neo4j" → Entities extracted, stored in Neo4j
- Q2: "How is it used in Graph RAG?" → Retrieves context from Neo4j based on entities

**Key Difference:**
- Baseline: Simple chronological history (loses context beyond 5 messages)
- Graph: Entity-driven retrieval (long-term memory persists across sessions)

## Architecture Overview

```
Frontend (Streamlit)
    ↓ HTTP POST /chat
Backend (FastAPI)
    ↓
Mode Router
    ├─→ Baseline Mode
    │   ├─ In-memory storage (deque, max 5)
    │   ├─ build_baseline_context()
    │   └─ Manual prompt construction
    │
    └─→ Graph Mode
        ├─ extract_entities() → {entities, topics}
        ├─ GraphRetriever.retrieve_context() → Neo4j query
        ├─ build_prompt() → Structured prompt
        └─ GraphMemory.write_interaction() → Neo4j write
    ↓
Gemini LLM
    ↓
Response returned to user
```

## Validation Checklist

- [x] Syntax error fixed in `backend/graph/graph.py`
- [x] `requirements.txt` created with all dependencies
- [x] Environment check script created (`check_environment.py`)
- [x] Comprehensive test suite created (`test_validation.py`)
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Neo4j database running
- [ ] Backend server starts without errors
- [ ] `/health` endpoint responds
- [ ] Baseline mode functional
- [ ] Graph mode functional
- [ ] Neo4j contains User/Event/Entity/Topic nodes
- [ ] Frontend connects to backend

## Manual Testing (Alternative)

### Using curl/PowerShell

**Health Check:**
```powershell
curl http://localhost:8000/health
```

**Baseline Mode:**
```powershell
$body = @{
    user_id = "test_user_baseline"
    message = "Explain Neo4j"
    mode = "baseline"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

**Graph Mode:**
```powershell
$body = @{
    user_id = "test_user_graph"
    message = "Explain Neo4j"
    mode = "graph"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

### Inspecting Neo4j Database

**Neo4j Browser:** http://localhost:7474

**Sample Queries:**
```cypher
// Count all nodes
MATCH (n) RETURN labels(n), count(n)

// View all users and their events
MATCH (u:User)-[:ASKED_ABOUT]->(e:Event)
RETURN u.id, e.content, e.timestamp
ORDER BY e.timestamp

// View entity relationships
MATCH (e:Event)-[:MENTIONS]->(ent:Entity)
RETURN e.content, collect(ent.name) as entities

// View topic relationships
MATCH (e:Event)-[:ASKED_ABOUT]->(t:Topic)
RETURN e.content, collect(t.name) as topics
```

## Known Issues & Limitations

### Non-Critical Issues Identified (DO NOT FIX - validation only):
1. `backend/rag/pipeline.py` contains unused stub functions
2. No `__init__.py` files in packages (works in Python 3.3+ but unusual)
3. Hardcoded `user_id = "demo_user"` in frontend
4. No connection pooling for Neo4j
5. No retry logic for failed API calls
6. Memory leak potential in baseline mode (unbounded user dictionary)

### These are acceptable for demo/academic submission and should NOT be refactored

## Final Validation Report

After running `test_validation.py`, you should see:

```
✓ SYSTEM READY FOR DEMO: YES
```

Or identify specific blocking issues to address.

## Troubleshooting

**Backend won't start:**
- Check all dependencies installed: `python check_environment.py`
- Verify no port conflicts on 8000
- Check import errors in terminal output

**Graph mode fails:**
- Verify Neo4j is running: `docker ps` or Neo4j Desktop
- Check Neo4j credentials in environment variables
- Test connection: Open Neo4j Browser at http://localhost:7474

**Gemini API errors:**
- Verify `GEMINI_API_KEY` is set and valid
- Check API quota/billing in Google Cloud Console
- Test with curl to Gemini API directly

**Tests fail:**
- Ensure backend is running before running tests
- Check terminal output for specific error messages
- Review individual test sections in output

## Success Criteria

For demo/submission readiness:
1. ✅ All dependencies installed
2. ✅ Backend starts without import errors
3. ✅ `/health` endpoint returns `{"status": "ok"}`
4. ✅ Baseline mode accepts and responds to messages
5. ✅ Graph mode writes to and retrieves from Neo4j
6. ✅ Behavioral difference observable (context usage)
7. ✅ Neo4j database contains expected node/relationship structure

## Next Steps After Validation

1. **If all tests pass:** System is ready for demo
2. **If minor warnings:** Document them, system still usable
3. **If critical failures:** Address blocking issues before demo
4. **No refactoring needed:** This is working prototype validation

---

**Validation Date:** January 15, 2026
**Validator Role:** Senior Engineer Onboarding
**Objective:** System verification without code modification
