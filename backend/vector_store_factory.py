"""
Vector store factory - chooses between Pinecone (local dev) and Vertex AI (production).
Provides separation of concerns between local and cloud environments.
"""

import os
from typing import Protocol, List, Dict, Any, Optional


class VectorStore(Protocol):
    """Protocol defining the vector store interface."""

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        ...

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        ...

    def upsert_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100):
        """Upload chunks with embeddings to vector store."""
        ...

    def search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Semantic search using query embedding."""
        ...

    def delete_all(self):
        """Delete all vectors from store."""
        ...


def get_vector_store() -> VectorStore:
    """
    Get appropriate vector store based on environment.

    Environment detection:
    - VECTOR_STORE=vertex → Vertex AI (Google Cloud production)
    - VECTOR_STORE=pinecone → Pinecone (local development)
    - Default (no env var) → Pinecone (backward compatible)

    Returns:
        VectorStore implementation (Pinecone or Vertex AI)
    """
    vector_store_type = os.getenv('VECTOR_STORE', 'pinecone').lower()

    if vector_store_type == 'vertex':
        # Google Cloud production - Vertex AI Vector Search
        print(f"🔵 Using Vertex AI Vector Search (Google Cloud)")
        from vector_store_vertex import get_vector_store as get_vertex_store
        return get_vertex_store()

    elif vector_store_type == 'pinecone':
        # Local development - Pinecone
        print(f"🟠 Using Pinecone Vector Store (Local Development)")
        from vector_store import get_vector_store as get_pinecone_store
        return get_pinecone_store()

    else:
        raise ValueError(
            f"Unknown VECTOR_STORE type: {vector_store_type}. "
            f"Must be 'vertex' or 'pinecone'"
        )
