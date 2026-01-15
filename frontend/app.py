import streamlit as st
import time

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Graph-Based RAG Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("Graph-Based RAG Chatbot")

# -------------------------------
# Mode Selector
# -------------------------------
mode = st.radio(
    "Select Retrieval Mode:",
    ("Baseline RAG", "Graph-RAG"),
    horizontal=True
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

