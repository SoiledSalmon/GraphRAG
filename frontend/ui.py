import streamlit as st
import time
import requests

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

</style>
""", unsafe_allow_html=True)

# -------------------------------
# Title Section
# -------------------------------
st.markdown("""
<h1>🧠 Graph-Based RAG Chatbot</h1>
<p style="text-align:center; color:#cccccc;">
Baseline RAG vs Graph-RAG using structured memory
</p>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar Controls
# -------------------------------
with st.sidebar:
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

# -------------------------------
# Initialize Chat History
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# Display Chat History
# -------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------
# Backend Integration
# -------------------------------
def get_backend_response(user_input, mode_selection):
    """
    Calls the real FastAPI backend to get a response.
    """
    url = "http://localhost:8000/chat"
    
    # Map UI selection to backend modes
    backend_mode = "graph" if "Graph-RAG" in mode_selection else "baseline"
    
    payload = {
        "user_id": "demo_user",
        "message": user_input,
        "mode": backend_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response received.")
    except Exception as e:
        return f"⚠️ Error: Could not connect to the backend at {url}. ({str(e)})"

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
            response = get_backend_response(user_input, mode)
            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
