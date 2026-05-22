"""
api/routes/chat.py
"""

from fastapi import APIRouter, HTTPException

from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse, ChatCitation
from app.services.workflow_service import execute_policy_workflow

router = APIRouter()

@router.post(
    "/ai/chat",
    response_model=ChatResponse,
    summary="Multi-Agent Policy Chat",
    description="Runs the 4-agent policy workflow (Classify -> Retrieve -> Risk Check -> Summarize).",
)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        # Run our new Capstone multi-agent pipeline
        result = execute_policy_workflow(
            prompt=request.prompt, 
            user_role=request.role,
            history=request.history
        )
        
        # Format citations
        citations = []
        for meta in result.get("metadatas", []):
            if meta and "source" in meta:
                citations.append(ChatCitation(
                    source=meta["source"], 
                    chunk=int(meta.get("chunk", 0)),
                    page=int(meta.get("page", 0)),
                    similarity=float(meta.get("similarity_score", 0.0))
                ))

        return ChatResponse(
            response=result["response"], 
            citations=citations,
            workflow_steps=result["workflow_steps"],
            confidence_score=result["confidence_score"],
            needs_review=result["needs_review"],
            intent_category=result.get("intent_category", "General"),
            intent_priority=result.get("intent_priority", "Low")
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred in workflow: {exc}",
        )
