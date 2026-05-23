"""
main.py
-------
Application entry-point.

Creates the FastAPI application instance and wires up all routers.

Run with:
    uvicorn app.main:app --reload
"""
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, chat, documents, auth

from app.services.audit_service import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() # Initialize SQLite Audit Log Database
    yield

# ---- Create the FastAPI app ----
app = FastAPI(
    title="DocuMind Enterprise Document RAG Backend",
    description="A powerful FastAPI backend that ingests PDFs into ChromaDB and layers semantic search into Groq LLM generations.",
    version="2.0.0",
    lifespan=lifespan
)

# ---- Configure CORS ----
# This allows our React frontend to communicate with this backend securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your Vercel frontend URL
    allow_credentials=False, # Must be False for wildcard origins in modern browsers
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Root route ----
# A quick sanity-check for students — just open http://localhost:8000/
@app.get("/", tags=["Root"])
def root():
    """Quick check that the server is alive."""
    return {"message": "DocuMind FastAPI Backend is running"}


# ---- Register routers ----
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])
