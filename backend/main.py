from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal

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
    Chat endpoint that accepts a message and mode, returning a placeholder response.
    """
    # DUMMY placeholder response as requested
    return ChatResponse(
        response="This is a placeholder response",
        context_used=[]
    )
