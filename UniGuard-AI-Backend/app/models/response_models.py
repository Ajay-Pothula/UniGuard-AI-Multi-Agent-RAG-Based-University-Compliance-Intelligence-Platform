"""
models/response_models.py
-------------------------
Pydantic models that describe the shape of API responses.
"""

from pydantic import BaseModel, Field
from typing import List

class ChatCitation(BaseModel):
    source: str
    chunk: int
    page: int = 0
    similarity: float = 0.0

class ChatResponse(BaseModel):
    """Response returned by the /ai/chat endpoint."""

    response: str = Field(
        ...,
        description="The assistant's reply from the LLM.",
    )
    citations: List[ChatCitation] = Field(
        default_factory=list,
        description="List of document citations used out of the vector database."
    )
    workflow_steps: List[str] = Field(
        default_factory=list,
        description="List of steps the multi-agent workflow took."
    )
    confidence_score: str = Field(
        default="N/A",
        description="Confidence of the compliance/risk agent."
    )
    needs_review: bool = Field(
        default=False,
        description="Flag indicating if an Admin should review this automatically."
    )
    intent_category: str = Field(
        default="General",
        description="Category classified by Agent 1."
    )
    intent_priority: str = Field(
        default="Low",
        description="Priority classified by Agent 1."
    )

class HealthResponse(BaseModel):
    """Response returned by the /health endpoint."""

    status: str = Field(
        ...,
        description="Current server status.",
        examples=["ok"],
    )
    message: str = Field(
        ...,
        description="Human-readable status message.",
        examples=["GenAI FastAPI backend is running."],
    )
