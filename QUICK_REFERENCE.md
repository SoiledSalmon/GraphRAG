# GraphRAG Validation - Quick Reference Card

## 🚀 Quick Start (After Reading This)

```powershell
# 1. Install everything (5 min)
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Set API key (required)
$env:GEMINI_API_KEY="your_key_here"

# 3. Start Neo4j (if using Docker)
docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

# 4. Start backend (Terminal 1)
cd backend
uvicorn backend.main:app --reload

# 5. Run validation (Terminal 2)
python test_validation.py

# 6. (Optional) Start frontend (Terminal 3)
streamlit run frontend/ui.py
```

## 📋 Validation Checklist

### Before Testing
- [ ] Run: `python check_environment.py` → Should show "✓ ENVIRONMENT READY"
- [ ] Neo4j accessible at http://localhost:7474
- [ ] GEMINI_API_KEY environment variable set

### During Testing
- [ ] Backend responds: `curl http://localhost:8000/health`
- [ ] Test suite runs: `python test_validation.py`
- [ ] All tests pass or show only warnings

### Success Indicators
- [ ] ✓ Health endpoint: 200 OK
- [ ] ✓ Baseline mode: 2 messages processed
- [ ] ✓ Graph mode: 2 messages with Neo4j writes
- [ ] ✓ Neo4j: User/Event/Entity/Topic nodes exist
- [ ] ✓ Final verdict: "SYSTEM READY FOR DEMO: YES"

## 🔧 Files Created During Validation

| File | Purpose |
|------|---------|
| `requirements.txt` | Dependencies specification |
| `check_environment.py` | Pre-flight environment check |
| `test_imports.py` | Syntax validation |
| `test_validation.py` | **Main test suite** ⭐ |
| `setup.bat` | Automated Windows setup |
| `VALIDATION_GUIDE.md` | Complete documentation |
| `VALIDATION_REPORT.txt` | Senior engineer assessment |
| `QUICK_REFERENCE.md` | This file |

## 🐛 Fixed Issues

- ✅ **backend/graph/graph.py line 15**: Removed extra quote in Cypher query
  - Before: `query = """"`
  - After: `query = """`

## 📊 Test Validation Flow

```
test_validation.py
├─ Test 1: Health Check
│  └─ GET /health → {"status": "ok"}
│
├─ Test 2: Baseline Mode
│  ├─ Q1: "Explain Neo4j"
│  └─ Q2: "How is it used in Graph RAG?"
│
├─ Test 3: Graph Mode
│  ├─ Q1: "Explain Neo4j"
│  └─ Q2: "How is it used in Graph RAG?"
│
├─ Test 4: Behavioral Difference
│  └─ Compare context usage between modes
│
└─ Test 5: Neo4j Inspection
   ├─ Node counts (User, Event, Entity, Topic)
   ├─ Relationship counts (ASKED_ABOUT, MENTIONS)
   └─ User event history verification
```

## 🎯 Expected Behavior

### Baseline Mode
- Stores last 5 messages in memory (deque)
- Context: chronological message history
- Loses context after 5 turns or server restart

### Graph Mode
- Extracts entities (spaCy NER) and topics (keywords)
- Stores in Neo4j: User → Event → Entity/Topic
- Retrieves context based on entity/topic matching
- Persists across sessions

### Key Difference
- **Baseline**: "What did I just say?" (short-term)
- **Graph**: "What do I know about X?" (long-term)

## 🔍 Manual Testing Commands

### Health Check
```powershell
Invoke-RestMethod http://localhost:8000/health
```

### Send Baseline Message
```powershell
$body = @{user_id="test1"; message="Hello"; mode="baseline"} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/chat -Method Post -Body $body -ContentType "application/json"
```

### Send Graph Message
```powershell
$body = @{user_id="test2"; message="Hello"; mode="graph"} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/chat -Method Post -Body $body -ContentType "application/json"
```

### Query Neo4j
```cypher
// Open http://localhost:7474 and run:
MATCH (u:User)-[:ASKED_ABOUT]->(e:Event)
RETURN u.id, e.content, e.timestamp
ORDER BY e.timestamp
```

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: No module named 'fastapi'" | Run: `python -m pip install -r requirements.txt` |
| "ModuleNotFoundError: No module named 'en_core_web_sm'" | Run: `python -m spacy download en_core_web_sm` |
| "Unable to retrieve routing information" (Neo4j) | Start Neo4j or check NEO4J_URI variable |
| "Invalid API key" (Gemini) | Set GEMINI_API_KEY environment variable |
| Backend won't start | Check port 8000 not in use: `netstat -ano \| findstr :8000` |
| Frontend can't connect | Ensure backend running on port 8000 |

## 📈 Success Metrics

### Minimum Viable Demo
- ✅ Backend starts
- ✅ Health check passes
- ✅ One mode works (baseline OR graph)

### Full Demo Ready
- ✅ Both modes work
- ✅ Graph writes to Neo4j
- ✅ Graph retrieves from Neo4j
- ✅ Behavioral difference visible

### Excellent Demo
- ✅ Frontend UI functional
- ✅ Multi-turn conversations work
- ✅ Neo4j browser shows graph structure
- ✅ All validation tests pass

## 🎓 Academic Submission Checklist

- [ ] Code runs without syntax errors (✓ Fixed)
- [ ] README or documentation exists (✓ VALIDATION_GUIDE.md)
- [ ] Both modes demonstrated
- [ ] Graph persistence shown
- [ ] No refactoring needed (per instructions)

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Install dependencies | 5 min |
| Configure environment | 2 min |
| Start Neo4j | 1-5 min |
| Start backend | 1 min |
| Run validation suite | 3-5 min |
| Manual testing | 5-10 min |
| **Total** | **20-30 min** |

## 🎬 Demo Script

1. **Show Frontend**: `streamlit run frontend/ui.py`
2. **Baseline Demo**:
   - Ask: "What is Neo4j?"
   - Ask: "How does it work with Python?"
   - Switch to Graph mode, clear history
3. **Graph Demo**:
   - Ask same questions
   - Show Neo4j browser with created nodes
   - Ask follow-up referencing earlier entities
4. **Compare**: Show how graph maintains long-term context

## 📞 Support Resources

- Validation Guide: `VALIDATION_GUIDE.md`
- Full Report: `VALIDATION_REPORT.txt`
- Environment Check: `python check_environment.py`
- Import Test: `python test_imports.py`
- Full Validation: `python test_validation.py`

---

**Last Updated**: January 15, 2026  
**Status**: Validation artifacts complete, ready for dependency installation  
**Next Step**: Run `setup.bat` or manual installation commands above
