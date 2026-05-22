"""
models/request_models.py
------------------------
Pydantic models that describe the shape of incoming API requests.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the sender (user or ai).")
    content: str = Field(..., description="Message content.")

class ChatRequest(BaseModel):
    """Body payload for the /ai/chat endpoint."""

    prompt: str = Field(
        ...,
        min_length=1,
        description="The user prompt to send to the LLM.",
        examples=["Explain what an API is in simple terms."],
    )
    history: List[ChatMessage] = Field(
        default_factory=list,
        description="The prior conversation history."
    )
    role: str = Field(
        default="Student",
        description="Role of the user (Student, Admin, Faculty) querying the policies."
    )
