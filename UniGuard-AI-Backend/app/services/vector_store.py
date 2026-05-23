import os
import chromadb
from chromadb.utils import embedding_functions
from pinecone import Pinecone, ServerlessSpec

# ---- Configuration ----
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "documind-index")

# Use Chroma's Default ONNX runtime (No PyTorch required, identically models all-MiniLM-L6-v2)
embedding_function = embedding_functions.DefaultEmbeddingFunction()

# Initialize Vector Storage
if PINECONE_API_KEY:
    # Use Pinecone (Cloud)
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Create index if it doesn't exist
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=384, # MiniLM-L6-v2 dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
        )
    index = pc.Index(PINECONE_INDEX_NAME)
    USE_PINECONE = True
else:
    # Fallback to ChromaDB (Local)
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name="documind_vectors",
        embedding_function=embedding_function
    )
    USE_PINECONE = False

def add_texts(texts: list[str], metadatas: list[dict], ids: list[str]):
    """
    Adds text chunks into the selected Vector Store.
    """
    if USE_PINECONE:
        # Pinecone requires vectors to be pre-computed OR we use the model here
        # For simplicity, we vectorize here using the same model
        embeddings = embedding_function(texts)
        vectors = []
        for i in range(len(texts)):
            # Gracefully handle numpy array casting from ONNX runtime to Pinecone native float list
            emb = embeddings[i].tolist() if hasattr(embeddings[i], 'tolist') else embeddings[i]
            vectors.append({
                "id": ids[i],
                "values": emb,
                "metadata": {**metadatas[i], "text": texts[i]}
            })
        index.upsert(vectors=vectors)
    else:
        collection.add(documents=texts, metadatas=metadatas, ids=ids)

def search_similar_with_metadata(query: str, n_results: int = 3):
    """
    Returns text chunks AND metadata from DB.
    """
    if USE_PINECONE:
        query_embedding = embedding_function([query])[0]
        results = index.query(
            vector=query_embedding,
            top_k=n_results,
            include_metadata=True
        )
        docs = [match["metadata"]["text"] for match in results["matches"]]
        metas = [match["metadata"] for match in results["matches"]]
        scores = [match["score"] for match in results["matches"]]
        return docs, metas, scores
    else:
        results = collection.query(
            query_texts=[query], 
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        if results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0]*len(docs)
            # Use inverse distance bounding so unnormalized L2 distances accurately reflect 0.0 to 1.0 Similarity
            scores = [1.0 / (1.0 + d) for d in distances]
            return docs, metas, scores
        return [], [], []

# ... Add or update other methods (get_all_documents, delete_document) as needed ...

def search_similar(query: str, n_results: int = 3) -> list[str]:
    """Legacy endpoint, returning only document text."""
    docs, _, _ = search_similar_with_metadata(query, n_results)
    return docs

def get_all_documents():
    """Gets all unique document filenames."""
    if USE_PINECONE:
        try:
            # Safely extract Pinecone metadata using a zero-vector sweep
            results = index.query(
                vector=[0.0] * 384,
                top_k=300,
                include_metadata=True
            )
            unique_sources = set()
            for match in results.get("matches", []):
                if "metadata" in match and "source" in match["metadata"]:
                    unique_sources.add(match["metadata"]["source"])
            return list(unique_sources)
        except Exception as e:
            print(f"Pinecone Sync Error: {e}")
            return []
    else:
        results = collection.get()
        if not results or not results.get("metadatas"):
            return []
        unique_sources = set()
        for meta in results["metadatas"]:
            if meta and "source" in meta:
                unique_sources.add(meta["source"])
        return list(unique_sources)

def delete_document(filename: str):
    """Deletes all chunks associated with a specific document."""
    if USE_PINECONE:
        index.delete(filter={"source": filename})
    else:
        collection.delete(where={"source": filename})
