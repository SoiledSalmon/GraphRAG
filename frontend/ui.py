import streamlit as st
import time
import requests
import pandas as pd

# -------------------------------
# Page Configuration (MUST BE FIRST)
# -------------------------------
st.set_page_config(
    page_title="Graph-Based RAG Chatbot",
    layout="wide"
)

# -------------------------------
# Custom CSS Styling
# -------------------------------
st.markdown("""
<style>

/* Main app background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Title */
h1 {
    text-align: center;
    font-weight: 700;
}

/* Chat input box */
textarea {
    border-radius: 12px !important;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.08);
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 10px;
}

/* Radio spacing */
.stRadio > div {
    gap: 20px;
}

/* Dashboard Cards */
.metric-card {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.card-graph {
    border-left: 5px solid #00f260; /* Neo Green */
    box-shadow: 0 0 15px rgba(0, 242, 96, 0.1);
}

.card-baseline {
    border-left: 5px solid #a770ef; /* Purple */
    box-shadow: 0 0 15px rgba(167, 112, 239, 0.1);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
}

.metric-label {
    font-size: 0.9rem;
    color: #cccccc;
    text-transform: uppercase;
    letter-spacing: 1px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# State Initialization
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "baseline_scores" not in st.session_state:
    st.session_state.baseline_scores = []

if "graph_scores" not in st.session_state:
    st.session_state.graph_scores = []

# -------------------------------
# Backend Integration
# -------------------------------
def get_backend_response(user_input, mode_selection):
    """
    Calls the real FastAPI backend to get a response.
    """
    # Use environment variable for backend URL, default to localhost
    import os
    url = os.getenv("BACKEND_URL", "http://localhost:8000/chat")
    
    # Map UI selection to backend modes
    backend_mode = "graph" if "Graph-RAG" in mode_selection else "baseline"
    
    payload = {
        "user_id": "demo_user",
        "message": user_input,
        "mode": backend_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "response": f"⚠️ Error: Could not connect to the backend at {url}. ({str(e)})",
            "crs_scores": None
        }

# -------------------------------
# Title
# -------------------------------
st.markdown("""
<h1>🧠 Graph-Based RAG Chatbot</h1>
<p style="text-align:center; color:#cccccc;">
Baseline RAG vs Graph-RAG using structured memory
</p>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar Navigation & Settings
# -------------------------------
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["💬 Chat Interface", "📊 CRS Dashboard"])
    
    st.divider()
    
    st.header("Settings")
    mode = st.radio(
        "🔀 Retrieval Mode",
        ("Baseline RAG (Text Memory)", "Graph-RAG (Graph Memory)")
    )
    st.markdown("---")
    st.markdown("""
    **Baseline RAG**
    Uses recent message history (last 5).

    **Graph-RAG**
    Uses entity relationships + context.
    """)
    
    if st.button("Clear History"):
        st.session_state.messages = []
        st.session_state.baseline_scores = []
        st.session_state.graph_scores = []
        st.rerun()

# -------------------------------
# Page Logic
# -------------------------------
if page == "💬 Chat Interface":
    # -------------------------------
    # Chat History
    # -------------------------------
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            


    # -------------------------------
    # Chat Input
    # -------------------------------
    user_input = st.chat_input("Ask a question...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                backend_data = get_backend_response(user_input, mode)
                
                response_text = backend_data.get("response", "No response")
                crs_data = backend_data.get("crs_scores")
                
                st.markdown(response_text)
                
                if crs_data:
                    # Update History for Dashboard
                    score_val = crs_data.get("composite_score", 0)
                    if "Graph-RAG" in mode:
                        st.session_state.graph_scores.append(score_val)
                    else:
                        st.session_state.baseline_scores.append(score_val)



        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "crs": crs_data
        })
        st.rerun() # Rerun to update dashboard immediately

elif page == "📊 CRS Dashboard":
    st.markdown("## Context Retention Score (CRS)")
    st.markdown("Measuring how well each system remembers user context.")
    
    # Info Box
    st.info("""
    **What is CRS?**
    CRS measures the percentage of stored context units (facts, entities, topics) that are correctly referenced 
    in the chatbot's responses. Higher scores indicate better memory retention.
    """)
    
    # Calculate Averages
    def get_avg(scores):
        return sum(scores) / len(scores) if scores else 0.0

    avg_graph = get_avg(st.session_state.graph_scores) * 100
    avg_base = get_avg(st.session_state.baseline_scores) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card card-graph">
            <h3 style="color:#00f260">🧠 Memory-Centric (Graph)</h3>
            <p class="metric-label">Average CRS</p>
            <p class="metric-value" style="color:#00f260">{avg_graph:.1f}%</p>
            <br>
            <p>Conversation Turns: {len(st.session_state.graph_scores)}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(avg_graph / 100)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card card-baseline">
            <h3 style="color:#a770ef">📄 RAG Baseline</h3>
            <p class="metric-label">Average CRS</p>
            <p class="metric-value" style="color:#a770ef">{avg_base:.1f}%</p>
            <br>
            <p>Conversation Turns: {len(st.session_state.baseline_scores)}</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(avg_base / 100)
    
    st.divider()
    
    # Detailed History Chart
    if st.session_state.graph_scores or st.session_state.baseline_scores:
        st.subheader("Session History")
        
        # Normalize lengths for chart
        max_len = max(len(st.session_state.graph_scores), len(st.session_state.baseline_scores))
        turns = range(1, max_len + 1)
        
        # Pad data
        g_data = st.session_state.graph_scores + [None] * (max_len - len(st.session_state.graph_scores))
        b_data = st.session_state.baseline_scores + [None] * (max_len - len(st.session_state.baseline_scores))
        
        df = pd.DataFrame({
            "Turn": turns,
            "Graph-RAG": g_data,
            "Baseline": b_data
        })
        
        st.line_chart(df, x="Turn", color=["#00f260", "#a770ef"])
