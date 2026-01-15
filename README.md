# GraphRAG
Linked-Memory Graphs Architectures to Enhance Contextual Adaptation in LLM-based Dialogue Systems 

graph-rag-dialogue-system/
│
├── backend/                     # 🔒 Backend logic (FastAPI)
│   ├── main.py                  # Entry point (API routes only)
│   ├── config.py                # Env vars, constants
│   │
│   ├── api/                     # API route definitions
│   │   └── chat.py
│   │
│   ├── graph/                   # 🧠 Graph Memory Layer
│   │   ├── __init__.py
│   │   ├── driver.py            # Neo4j connection
│   │   ├── schema.py            # Node & relationship definitions
│   │   ├── insert.py            # Graph write operations
│   │   └── retrieve.py          # Graph traversal logic
│   │
│   ├── rag/                     # 🔍 RAG Logic
│   │   ├── __init__.py
│   │   ├── extractor.py         # Entity & topic extraction
│   │   ├── prompt_builder.py    # Prompt construction
│   │   ├── baseline.py          # Normal RAG (no graph)
│   │   └── graph_rag.py          # Graph-based RAG pipeline
│   │
│   ├── llm/                     # 🤖 LLM Integration
│   │   ├── __init__.py
│   │   └── gemini_client.py
│   │
│   ├── models/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   └── chat_models.py
│   │
│   └── utils/                   # Helper utilities
│       └── logger.py
│
├── frontend/                    # 🎨 Streamlit UI
│   ├── app.py
│   └── api_client.py
│
├── evaluation/                  # 📊 Experiments & results
│   ├── test_conversations.md
│   ├── evaluation_metrics.md
│   └── results.md
│
├── docs/                        # 📄 Documentation & PPT content
│   ├── architecture.md
│   ├── methodology.md
│   ├── system_design.md
│   └── screenshots/
│
├── scripts/                     # 🔧 One-time utilities
│   ├── init_graph.cypher
│   └── reset_graph.py
│
├── .env                         # 🔐 Secrets (NOT committed)
├── .gitignore
├── README.md
└── requirements.txt

