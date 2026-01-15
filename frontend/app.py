import streamlit as st
import time
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
    background-color: rgba(255, 255, 255, 0.05);
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
}

/* Radio buttons spacing */
.stRadio > div {
    gap: 20px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Graph-Based RAG Chatbot",
    layout="wide"
)

st.markdown("""
<h1>🧠 Graph-Based RAG Chatbot</h1>
<p style="text-align:center; color:#cccccc;">
Baseline RAG vs Graph-RAG using structured memory
</p>
""", unsafe_allow_html=True)

# -------------------------------
# Mode Selector
# -------------------------------

with st.sidebar:
    st.header("Settings")
    mode = st.radio(
    "🔀 Retrieval Mode",
    ("Baseline RAG (Text Memory)", "Graph-RAG (Graph Memory)"),
    horizontal=True
)
    st.markdown("<hr style='border:1px solid #444;'>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        """
        **Baseline RAG**  
        Uses vector similarity only.

        **Graph-RAG**  
        Uses entity relationships + context.
        """
    )

st.markdown("---")

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
    """
    Temporary mock function.
    Replace this with FastAPI call later.
    """
    time.sleep(1)

    if mode == "Graph-RAG":
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
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_mock_response(user_input, mode)
            st.markdown(response)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

