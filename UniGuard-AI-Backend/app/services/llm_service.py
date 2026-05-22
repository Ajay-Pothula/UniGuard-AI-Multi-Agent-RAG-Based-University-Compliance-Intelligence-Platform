"""
services/llm_service.py
-----------------------
Service layer that handles communication with the LLM API.
"""

import requests
from fastapi import HTTPException
from typing import List, Tuple

from app.core.config import GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL
from app.services.vector_store import search_similar_with_metadata
from app.models.request_models import ChatMessage

def ask_llm(prompt: str, history: List[ChatMessage] = None) -> Tuple[str, list]:
    """
    RAG-enabled LLM call. Searches ChromaDB for semantic matches 
    to the prompt, and injects that context into the LLM payload.
    It also accepts a history list for conversation memory.
    """
    if history is None:
        history = []

    # --- Guard: ensure the API key is available ---
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=400,
            detail=(
                "GROQ_API_KEY is not set. "
                "Please add it to your .env file and restart the server."
            ),
        )

    # --- 1. Retrieve Context from Vector Store ---
    try:
        relevant_chunks, metadatas = search_similar_with_metadata(prompt, n_results=3)
        context_text = "\n\n---\n\n".join(relevant_chunks)
    except Exception as e:
        print(f"Warning: Vector search failed: {e}")
        context_text = ""
        metadatas = []

    # --- 2. Construct the RAG Prompt ---
    system_message = (
        "You are DocuMind, an expert enterprise AI assistant. "
        "Answer the user's question based strictly on the provided Context. "
        "If the answer is not contained within the Context, say 'I cannot answer this based on the provided documents.'\n\n"
        f"CONTEXT:\n{context_text}"
    )

    # --- 3. Build the Memory Array ---
    messages = [{"role": "system", "content": system_message}]
    
    for msg in history:
        # Map our roles (user/ai) to Groq roles (user/assistant)
        role = "assistant" if msg.role == "ai" else "user"
        messages.append({"role": role, "content": msg.content})

    # Append current prompt
    messages.append({"role": "user", "content": prompt})

    # --- Build the request ---
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
    }

    # --- Call the LLM API ---
    try:
        response = requests.post(
            GROQ_BASE_URL,
            headers=headers,
            json=payload,
            timeout=30,  # seconds — prevents hanging if the API is slow
        )
    except requests.Timeout:
        raise HTTPException(
            status_code=504,
            detail="LLM API request timed out. Try again or increase the timeout.",
        )
    except requests.ConnectionError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not connect to the LLM API. Check your network or GROQ_BASE_URL: {exc}",
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM API request failed: {exc}",
        )

    # --- Handle non-2xx responses ---
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=(
                f"LLM API returned status {response.status_code}: "
                f"{response.text}"
            ),
        )

    # --- Extract the assistant message ---
    data = response.json()

    try:
        assistant_message: str = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unexpected response structure from LLM API: {exc}",
        )

    return assistant_message, metadatas
