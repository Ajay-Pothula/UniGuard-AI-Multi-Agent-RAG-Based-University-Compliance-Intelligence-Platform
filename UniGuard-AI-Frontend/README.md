# DocuMind - Enterprise Document RAG Platform

DocuMind is a top-tier **Retrieval-Augmented Generation (RAG)** application built to allow seamless, intelligent chatting with uploaded enterprise documents. Designed with a robust FastAPI backend and a stunning, glassmorphism-inspired React frontend, it demonstrates industry-level Machine Learning and Software Engineering practices.

## 🚀 Key Features

*   **🧠 Stateless Chat Memory:** The React frontend maps and securely transmits conversational state context dynamically to the FastAPI backend, ensuring the LLM never loses track of the conversation without relying on heavy backend session storage.
*   **📑 Verifiable Source Citations:** To eliminate LLM hallucinations, the ChromaDB vector search extracts exact document metadata alongside semantic chunks. The UI renders precise glowing **Source Badges** for every single answer retrieved from the knowledge base.
*   **🗂️ Dynamic Document Management:** Exposed REST endpoints allow the frontend to seamlessly query underlying vector metadata. Users can view active enterprise documents and selectively delete PDFs directly from the vector store via the UI.
*   **💎 Visual Excellence:** A highly-polished "Electric Cyan" dark theme featuring native CSS glassmorphism, pulse animations, responsive typography, and `react-markdown` support for beautiful AI responses (code blocks, bullet points, headers).

## 🛠️ Tech Stack

**Frontend (React):**
*   Vite + React (JavaScript)
*   Vanilla CSS (CSS Custom Properties, Glassmorphism, CSS Animations)
*   `lucide-react` (SVG Icons)
*   `react-markdown` (Rich Text Parsing)

**Backend (Python/FastAPI):**
*   FastAPI & Uvicorn (High-performance API routing)
*   PyMuPDF (`fitz`) (Fast PDF text extraction)
*   LangChain (Text Splitting / Chunking)
*   ChromaDB (Persistent Vector Database)
*   Sentence Transformers (`all-MiniLM-L6-v2`) (Lightning-fast local CPU embeddings)
*   Groq API (Ultra-low latency LLM generation)

---

## ⚙️ How to Run Locally

DocuMind runs as two separate services: the FastAPI Python backend and the React Vite frontend.

### 1. Start the FastAPI Backend
Ensure you have cloned or downloaded the backend repository (e.g., `DocuMind Enterprise Document RAG Backend`).

```bash
# 1. Navigate to the backend directory
cd "DocuMind Enterprise Document RAG Backend"

# 2. Activate your virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Create a .env file and add your Groq API Key
echo "GROQ_API_KEY=your_key_here" > .env

# 4. Start the Uvicorn Server
uvicorn app.main:app --reload
```
*The backend will boot up and run on `http://localhost:8000`.*

### 2. Start the React Frontend
Open a new terminal window for the frontend.

```bash
# 1. Navigate to the frontend directory
cd DocuMind-Frontend

# 2. Install dependencies
npm install

# 3. Start the Vite Dev Server
npm run dev
```
*The frontend will boot up and run on `http://localhost:5173`. Open this URL in your browser to begin chatting!*

---

## 🏗️ Architecture & RAG Pipeline

1. **Ingestion (`/documents/upload`):** 
   - A user uploads a PDF. The FastAPI backend reads the raw bytes, parses the text using PyMuPDF, and splits the string using Langchain's `RecursiveCharacterTextSplitter` (1000 chunk size, 200 overlap).
   - The chunks are embedded locally using `SentenceTransformers` and saved into **ChromaDB** along with metadata (filename and chunk index).
2. **Retrieval & Generation (`/ai/chat`):**
   - The React frontend sends the user's prompt alongside the entire chat history. 
   - The backend converts the string prompt into a vector and queries ChromaDB (`search_similar_with_metadata`).
   - The Top 3 most semantically similar chunks (and their metadata) are extracted.
   - The chunks are injected into a highly restricted **System Prompt** telling the LLM to *only* use the provided context.
   - The prompt, context, and history are shipped to the **Groq API** for lightning-fast inference.
3. **Response:** 
   - The generated answer and the source citations are returned to the React App, mapping seamlessly to the floating Chat UI.

---
*Built by Pothula Ajay — Machine Learning Engineer & Software Developer.*
