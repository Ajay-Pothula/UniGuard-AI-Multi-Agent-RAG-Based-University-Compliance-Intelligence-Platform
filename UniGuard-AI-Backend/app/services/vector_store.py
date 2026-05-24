import os

# ---- Configuration ----
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "documind-index")

USE_PINECONE = bool(PINECONE_API_KEY)

# Lazy Singletons
_pc_index = None
_chroma_collection = None
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        from chromadb.utils import embedding_functions
        _embedder = embedding_functions.DefaultEmbeddingFunction()
    return _embedder

def get_pinecone_index():
    global _pc_index
    if _pc_index is None:
        from pinecone import Pinecone, ServerlessSpec
        pc = Pinecone(api_key=PINECONE_API_KEY)
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=PINECONE_INDEX_NAME, dimension=384, metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
            )
        _pc_index = pc.Index(PINECONE_INDEX_NAME)
    return _pc_index

def get_chroma_collection():
    global _chroma_collection
    if _chroma_collection is None:
        import chromadb
        DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
        client = chromadb.PersistentClient(path=DB_PATH)
        _chroma_collection = client.get_or_create_collection(name="documind_vectors", embedding_function=get_embedder())
    return _chroma_collection

def add_texts(texts: list[str], metadatas: list[dict], ids: list[str]):
    """
    Adds text chunks into the selected Vector Store.
    """
    if USE_PINECONE:
        embedder = get_embedder()
        pc_index = get_pinecone_index()
        # Pinecone requires vectors to be pre-computed OR we use the model here
        # Batch the texts so ONNX doesn't spike RAM trying to embed 150 chunks at once
        embeddings = []
        batch_size = 15
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            embeddings.extend(embedder(batch_texts))
            
        vectors = []
        for i in range(len(texts)):
            # Gracefully handle numpy array casting from ONNX runtime to Pinecone native float list
            emb = embeddings[i].tolist() if hasattr(embeddings[i], 'tolist') else embeddings[i]
            vectors.append({
                "id": ids[i],
                "values": emb,
                "metadata": {**metadatas[i], "text": texts[i]}
            })
            
        # Pinecone upsert limit is ~100 per API request
        for i in range(0, len(vectors), 50):
            pc_index.upsert(vectors=vectors[i:i+50])
    else:
        chroma_collection = get_chroma_collection()
        chroma_collection.add(documents=texts, metadatas=metadatas, ids=ids)

def search_similar_with_metadata(query: str, n_results: int = 3):
    """
    Returns text chunks AND metadata from DB.
    """
    if USE_PINECONE:
        embedder = get_embedder()
        pc_index = get_pinecone_index()
        query_embedding = embedder([query])[0]
        # Make sure query_embedding is correctly formatted as a list for Pinecone
        query_embedding_list = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding
        results = pc_index.query(
            vector=query_embedding_list,
            top_k=n_results,
            include_metadata=True
        )
        docs = [match["metadata"]["text"] for match in results["matches"]]
        metas = [match["metadata"] for match in results["matches"]]
        scores = [match["score"] for match in results["matches"]]
        return docs, metas, scores
    else:
        chroma_collection = get_chroma_collection()
        results = chroma_collection.query(
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
        pc_index = get_pinecone_index()
        try:
            # Safely extract Pinecone metadata using a zero-vector sweep
            # Increase top_k to 10000 to scan the maximum chunk radius, supporting 200+ PDFs without clipping.
            results = pc_index.query(
                vector=[0.0] * 384,
                top_k=10000,
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
        chroma_collection = get_chroma_collection()
        results = chroma_collection.get()
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
        pc_index = get_pinecone_index()
        pc_index.delete(filter={"source": filename})
    else:
        chroma_collection = get_chroma_collection()
        chroma_collection.delete(where={"source": filename})
