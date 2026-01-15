import streamlit as st
import time

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
    Uses vector similarity only.

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
# Mock Backend Response
# -------------------------------
def get_mock_response(user_input, mode):
    time.sleep(1)

    if "Graph-RAG" in mode:
        return (
            "📌 **Graph-RAG Response**\n\n"
            "This answer uses structured graph memory to retrieve "
            "related entities, past interactions, and connected topics, "
            "resulting in better contextual continuity."
        )
    else:
        return (
            "📄 **Baseline RAG Response**\n\n"
            "This answer is generated using recent text context only, "
            "without considering relationships between past interactions."
        )

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
            response = get_mock_response(user_input, mode)
            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
