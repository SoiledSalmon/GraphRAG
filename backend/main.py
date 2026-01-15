from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal, Any, Dict
import os

# Internal module integrations
from .rag.extractor import extract_entities
from .graph.retriever import GraphRetriever
from .rag.baseline import add_user_message, build_baseline_context
from .rag.prompt_builder import build_prompt
from .llm.gemini_client import generate_response

app = FastAPI()

# Request model for the chat endpoint
class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: Literal["graph", "baseline"]

# Response model for the chat endpoint
class ChatResponse(BaseModel):
    response: str
    context_used: List[str]

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint integrating the RAG pipeline with explicit mode paths.
    """
    # a) Extract entities and topics
    extraction = extract_entities(request.message)
    entities = extraction.get("entities", [])
    topics = extraction.get("topics", [])

    prompt = ""

    # b) IF mode == "graph"
    if request.mode == "graph":
        try:
            # Instantiate GraphRetriever using env vars
            uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            username = os.environ.get("NEO4J_USERNAME", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "password")
            
            retriever = GraphRetriever(uri, username, password)
            try:
                graph_context = retriever.retrieve_context(
                    request.user_id, 
                    entities, 
                    topics
                )
                # Use build_prompt ONLY for graph mode dictionary context
                prompt = build_prompt(graph_context, request.message)
            finally:
                retriever.close()
        except Exception:
            # Return safe error message if graph retrieval fails
            return ChatResponse(
                response="The system is temporarily unavailable due to a graph error.",
                context_used=[]
            )

    # c) IF mode == "baseline"
    elif request.mode == "baseline":
        add_user_message(request.user_id, request.message)
        baseline_context = build_baseline_context(request.user_id)
        
        # Explicit construction for baseline string context (bypasses build_prompt)
        prompt = f"{baseline_context}\n\nUser Query:\n{request.message}"

    # d) Send the prompt to the LLM
    llm_response = generate_response(prompt)

    # e) Return the LLM response
    return ChatResponse(
        response=llm_response,
        context_used=entities + topics
    )
