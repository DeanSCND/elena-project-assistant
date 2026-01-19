"""
Vector store for semantic search using Qdrant + OpenAI embeddings.
Works identically for local development and Google Cloud production.
"""

import os
import time
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI

# Configuration
COLLECTION_NAME = "elena_construction_docs"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Qdrant URL - environment-based
QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')

# Lazy initialization
qdrant_client = None
openai_client = None


class QdrantVectorStore:
    """Manages vector embeddings and semantic search using Qdrant."""

    def __init__(self):
        global qdrant_client, openai_client

        # Initialize clients on first use
        if qdrant_client is None:
            print(f"Connecting to Qdrant at {QDRANT_URL}...")
            qdrant_client = QdrantClient(url=QDRANT_URL, timeout=60)
            print(f"✓ Connected to Qdrant")

        if openai_client is None:
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment")
            # Strip whitespace to handle secrets with trailing newlines
            openai_client = OpenAI(api_key=OPENAI_API_KEY.strip())

        self.client = qdrant_client
        self._init_collection()

    def _init_collection(self):
        """Initialize or connect to Qdrant collection."""
        print(f"{'='*80}")
        print(f"QDRANT VECTOR STORE INITIALIZATION")
        print(f"{'='*80}")
        print(f"  Qdrant URL: {QDRANT_URL}")

        # Check if collection exists
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME not in collection_names:
            # Create collection
            print(f"  Creating new collection: {COLLECTION_NAME}")
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            print(f"✓ Collection created: {COLLECTION_NAME}")
        else:
            print(f"✓ Using existing collection: {COLLECTION_NAME}")

        # Get collection info
        collection_info = self.client.get_collection(COLLECTION_NAME)
        vector_count = collection_info.points_count

        print(f"  Vector count: {vector_count}")
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
                pass  # Removed blocking sleep - OpenAI has rate limiting built-in

        return embeddings

    def upsert_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100):
        """
        Upload chunks with embeddings to Qdrant.

        Args:
            chunks: List of dicts with {id, content, metadata}
            batch_size: Number of vectors to upsert at once
        """
        print(f"\n{'='*80}")
        print(f"UPLOADING {len(chunks)} CHUNKS TO QDRANT")
        print(f"{'='*80}")

        # Check if already uploaded
        collection_info = self.client.get_collection(COLLECTION_NAME)
        existing_count = collection_info.points_count

        if existing_count >= len(chunks):
            print(f"✓ Collection already contains {existing_count} vectors (expected {len(chunks)})")
            print(f"  Skipping upload. Delete collection to re-upload.")
            return

        # Generate embeddings
        print(f"\nGenerating embeddings...")
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)

        # Prepare points for upload
        points = []
        id_mapping = {}  # Store mapping of UUIDs to original IDs

        for i, chunk in enumerate(chunks):
            # Generate deterministic UUID from original ID
            chunk_id_str = chunk['id']
            # UUID v5 (SHA-1 namespace-based) - deterministic and unique
            chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id_str))

            # Clean metadata - convert None to empty string
            clean_metadata = {}
            for key, value in chunk['metadata'].items():
                if value is not None:
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = ""

            # Add original ID and content preview to metadata
            clean_metadata['original_id'] = chunk_id_str
            clean_metadata['content_preview'] = chunk['content'][:500]

            # Store mapping
            id_mapping[chunk_uuid] = chunk_id_str

            points.append(
                PointStruct(
                    id=chunk_uuid,
                    vector=embeddings[i],
                    payload=clean_metadata
                )
            )

        # Upload in batches
        print(f"\nUploading vectors to Qdrant...")
        uploaded_count = 0

        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            batch_num = i // batch_size + 1

            try:
                self.client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=batch
                )
                uploaded_count += len(batch)
                print(f"  Batch {batch_num}: Uploaded {i+1}-{min(i+batch_size, len(points))} of {len(points)}")
                # Removed blocking sleep - Qdrant handles rate limiting

            except Exception as e:
                print(f"  ✗ ERROR uploading batch {batch_num}: {type(e).__name__}: {e}")
                raise

        # Verify upload (Qdrant updates are synchronous, no delay needed)
        final_info = self.client.get_collection(COLLECTION_NAME)
        final_count = final_info.points_count

        print(f"\n{'='*80}")
        print(f"UPLOAD SUMMARY:")
        print(f"  Total vectors processed: {uploaded_count}")
        print(f"  Total vectors in collection: {final_count}")

        if final_count < len(chunks):
            print(f"\n  ✗ MISMATCH: Expected {len(chunks)}, got {final_count}")
            print(f"    Missing: {len(chunks) - final_count} vectors")
        else:
            print(f"  ✓ Upload complete!")

        print(f"{'='*80}\n")

    def search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Semantic search using query embedding.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter: Metadata filter (Qdrant supports rich filtering)

        Returns:
            List of {id, score, metadata} dicts
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Search Qdrant using query_points
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=top_k
        )

        # Format results - restore original IDs from metadata
        formatted_results = []
        for hit in results.points:
            formatted_results.append({
                'id': hit.payload.get('original_id', str(hit.id)),
                'score': hit.score,
                'metadata': hit.payload
            })

        return formatted_results

    def delete_all(self):
        """Delete all vectors from collection (for re-indexing)."""
        print(f"Deleting collection: {COLLECTION_NAME}")
        self.client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"✓ Collection deleted")
        # Recreate empty collection
        self._init_collection()


# Singleton instance
_vector_store = None

def get_vector_store() -> QdrantVectorStore:
    """Get or create QdrantVectorStore singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = QdrantVectorStore()
    return _vector_store
