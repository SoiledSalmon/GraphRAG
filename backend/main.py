from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal, Any, Dict, Optional
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

load_dotenv()  # Load .env before any os.environ.get() calls

logger = logging.getLogger(__name__)

# Internal module integrations
from .rag.extractor import extract_entities
from .graph.retriever import GraphRetriever
from .graph.graph import GraphMemory
from .rag.baseline import add_user_message, build_baseline_context
from .rag.prompt_builder import build_prompt
from .llm.gemini_client import generate_response
from .evaluation.crs_evaluator import CRSEvaluator, CRSScores

app = FastAPI()

# Request model for the chat endpoint
class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: Literal["graph", "baseline"]

# Initialize CRS Evaluator
crs_evaluator = CRSEvaluator()

# Response model for the chat endpoint
class ChatResponse(BaseModel):
    response: str
    context_used: List[str]
    crs_scores: Optional[CRSScores] = None

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok"}

def _format_graph_context(context: Dict[str, Any]) -> str:
    """
    Helper to format graph context into a string for CRS evaluation.
    Replicates logic from prompt_builder.py to ensure consistency without modifying it.
    """
    memory_lines = []
    past_events = context.get("past_events", [])
    if past_events:
        for event in past_events:
            entity = event.get("entity")
            if entity:
                memory_lines.append(f"- Previously, the user mentioned the entity \"{entity}\" in a query.")

    entity_count = context.get("entity_count", 0)
    topic_count = context.get("topic_count", 0)
    
    if entity_count > 0 or topic_count > 0:
        count_summary = "- The conversation includes"
        parts = []
        if entity_count > 0:
            parts.append(f"{entity_count} distinct entities")
        if topic_count > 0:
            parts.append(f"{topic_count} topics")
        
        count_summary += " " + " and ".join(parts) + "."
        memory_lines.append(count_summary)

    return "\n".join(memory_lines)

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
            
            # Retrieve THEN Write: We want context from past events, not the current one.
            try:
                memory = GraphMemory(uri, username, password)
                memory.write_interaction(request.user_id, request.message, entities, topics)
                memory.close()
            except Exception as e:
                logger.warning("Graph write failed (non-blocking): %s", e)
        except Exception as e:
            logger.error("Graph retrieval failed: %s", e)
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

    # e) Calculate CRS Scores
    # We need the context text.
    context_text = ""
    if request.mode == "baseline":
        # For baseline, we rebuild it or capture it. 
        # (Ideally we captured it above, but to avoid large refactors we rebuild/access it here)
        # Note: baseline_context is available in this scope if mode==baseline
        context_text = locals().get("baseline_context", "")
    elif request.mode == "graph":
        # For graph, we format the context dictionary
        # graph_context is available in local scope
        context_text = _format_graph_context(locals().get("graph_context", {}))

    crs = crs_evaluator.evaluate(
        query_text=request.message,
        response_text=llm_response,
        context_text=context_text,
        extract_func=extract_entities
    )

    # f) Return the LLM response
    return ChatResponse(
        response=llm_response,
        context_used=entities + topics,
        crs_scores=crs
    )
