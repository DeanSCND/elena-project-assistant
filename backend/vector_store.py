"""
Vector store for semantic search using Pinecone + OpenAI embeddings.
"""

import os
import time
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import numpy as np

# Initialize clients
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in environment")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment")

pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Configuration
INDEX_NAME = "elena-construction-docs"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
CLOUD = "aws"
REGION = "us-east-1"


class VectorStore:
    """Manages vector embeddings and semantic search."""

    def __init__(self):
        self.index = None
        self._init_index()

    def _init_index(self):
        """Initialize or connect to Pinecone index."""
        print(f"{'='*80}")
        print(f"PINECONE VECTOR STORE INITIALIZATION")
        print(f"{'='*80}")

        # Check if index exists
        existing_indexes = [idx.name for idx in pc.list_indexes()]

        if INDEX_NAME not in existing_indexes:
            print(f"Creating new index: {INDEX_NAME}")
            pc.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=CLOUD,
                    region=REGION
                )
            )
            print(f"✓ Index created: {INDEX_NAME}")

            # Wait for index to be ready
            while not pc.describe_index(INDEX_NAME).status['ready']:
                print("  Waiting for index to be ready...")
                time.sleep(1)
        else:
            print(f"✓ Using existing index: {INDEX_NAME}")

        self.index = pc.Index(INDEX_NAME)

        # Get stats
        stats = self.index.describe_index_stats()
        print(f"  Vector count: {stats.get('total_vector_count', 0)}")
        print(f"  Dimension: {EMBEDDING_DIMENSION}")
        print(f"  Model: {EMBEDDING_MODEL}")
        print(f"{'='*80}\n")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using OpenAI."""
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"  Generating embeddings {i+1}-{min(i+batch_size, len(texts))} of {len(texts)}")

            response = openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch
            )

            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)

            # Rate limiting
            if i + batch_size < len(texts):
                time.sleep(0.1)

        return embeddings

    def upsert_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100):
        """
        Upload chunks with embeddings to Pinecone.

        Args:
            chunks: List of dicts with {id, content, metadata}
            batch_size: Number of vectors to upsert at once
        """
        print(f"\n{'='*80}")
        print(f"UPLOADING {len(chunks)} CHUNKS TO PINECONE")
        print(f"{'='*80}")

        # Check if already uploaded
        stats = self.index.describe_index_stats()
        existing_count = stats.get('total_vector_count', 0)

        if existing_count >= len(chunks):
            print(f"✓ Index already contains {existing_count} vectors (expected {len(chunks)})")
            print(f"  Skipping upload. Delete index to re-upload.")
            return

        # Generate embeddings
        print(f"\nGenerating embeddings...")
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)

        # Prepare vectors for upload
        vectors = []
        for i, chunk in enumerate(chunks):
            vectors.append({
                'id': chunk['id'],
                'values': embeddings[i],
                'metadata': {
                    **chunk['metadata'],
                    'content_preview': chunk['content'][:500]  # Store preview for debugging
                }
            })

        # Upload in batches
        print(f"\nUploading vectors to Pinecone...")
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"  Uploaded {i+1}-{min(i+batch_size, len(vectors))} of {len(vectors)}")
            time.sleep(0.1)  # Rate limiting

        print(f"\n✓ Upload complete!")
        print(f"  Total vectors: {len(vectors)}")
        print(f"{'='*80}\n")

    def search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Semantic search using query embedding.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter: Metadata filter (e.g., {"source_pdf": "F1.1"})

        Returns:
            List of {id, score, metadata} dicts
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )

        # Format results
        formatted_results = []
        for match in results.matches:
            formatted_results.append({
                'id': match.id,
                'score': match.score,
                'metadata': match.metadata
            })

        return formatted_results

    def delete_all(self):
        """Delete all vectors from index (for re-indexing)."""
        print(f"Deleting all vectors from {INDEX_NAME}...")
        self.index.delete(delete_all=True)
        print(f"✓ Index cleared")


# Singleton instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create VectorStore singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
