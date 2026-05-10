from __future__ import annotations

"""Vector store using ChromaDB with sentence-transformers embeddings.

Implements a proper embedding + vector database pipeline:
1. Text chunks are embedded using sentence-transformers (all-MiniLM-L6-v2)
2. Embeddings are stored in ChromaDB (persistent on disk)
3. Queries are embedded with the same model and matched via cosine similarity
4. Results include page number and section metadata for citations

ChromaDB provides:
- Persistent vector storage on disk
- Efficient similarity search with HNSW indexing
- Metadata filtering by document_id
"""

import os

import config
from pdf_processor import TextChunk


# --- Embedding Model (Gemini) ---
_gemini_configured = False

def _configure_gemini():
    """Lazy-configure Google Gemini API."""
    global _gemini_configured
    if not _gemini_configured:
        import google.generativeai as genai
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing in environment variables.")
        genai.configure(api_key=config.GEMINI_API_KEY)
        _gemini_configured = True
        print(f"[INFO] Configured Gemini for embeddings using {config.EMBEDDING_MODEL}.")


# --- ChromaDB Client ---
_chroma_client = None


def _get_chroma():
    """Lazy-initialize the ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        os.makedirs(config.CHROMA_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    return _chroma_client


def _get_collection(document_id: str):
    """Get or create a ChromaDB collection for a document."""
    client = _get_chroma()
    # Each document gets its own collection for clean isolation
    collection_name = f"doc_{document_id.replace('-', '_')}"
    # Truncate to ChromaDB's 63-char limit
    collection_name = collection_name[:63]
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def _embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using Google Gemini."""
    _configure_gemini()
    import google.generativeai as genai
    
    # Gemini embed_content works with a list of strings
    result = genai.embed_content(
        model=config.EMBEDDING_MODEL,
        content=texts,
        task_type="retrieval_document",
        output_dimensionality=768
    )
    return result['embedding']


def _embed_query(query: str) -> list[float]:
    """Embed a single query using Google Gemini."""
    _configure_gemini()
    import google.generativeai as genai
    
    result = genai.embed_content(
        model=config.EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query",
        output_dimensionality=768
    )
    return result['embedding']


def store_chunks(chunks: list[TextChunk]) -> int:
    """Embed and store text chunks in ChromaDB.

    Args:
        chunks: List of TextChunk objects from pdf_processor.

    Returns:
        Number of chunks stored.
    """
    if not chunks:
        return 0

    document_id = chunks[0].document_id
    collection = _get_collection(document_id)

    # Prepare data for ChromaDB
    ids = [c.chunk_id for c in chunks]
    texts = [c.text for c in chunks]
    metadatas = [
        {
            "page_number": c.page_number,
            "section": c.section or "",
            "document_id": c.document_id,
        }
        for c in chunks
    ]

    # Generate embeddings locally via sentence-transformers
    print(f"[INFO] Generating embeddings for {len(texts)} chunks...")
    embeddings = _embed_texts(texts)

    # Store in ChromaDB
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"[INFO] Stored {len(chunks)} chunks in ChromaDB collection for doc {document_id[:8]}...")
    return len(chunks)


def query_chunks(
    document_id: str,
    query_text: str,
    top_k: int = config.TOP_K_RESULTS,
) -> list[dict]:
    """Retrieve the most relevant chunks for a query.

    Args:
        document_id: Which document to search within.
        query_text: The user's question.
        top_k: Number of results to return.

    Returns:
        List of dicts with 'text', 'page_number', 'section', 'distance'.
    """
    collection = _get_collection(document_id)

    # Embed the query
    query_embedding = _embed_query(query_text)

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Format results
    output = []
    if results and results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            output.append({
                "text": doc,
                "page_number": meta["page_number"],
                "section": meta.get("section") or None,
                "distance": distance,
            })

    return output


def delete_document(document_id: str) -> bool:
    """Delete a document's collection from ChromaDB.

    Args:
        document_id: The document to remove.

    Returns:
        True if deletion succeeded.
    """
    try:
        client = _get_chroma()
        collection_name = f"doc_{document_id.replace('-', '_')}"[:63]
        client.delete_collection(name=collection_name)
        return True
    except Exception:
        return False


def document_exists(document_id: str) -> bool:
    """Check if a document has been indexed in ChromaDB."""
    try:
        collection = _get_collection(document_id)
        return collection.count() > 0
    except Exception:
        return False
