"""
Vector store for semantic search using Pinecone + OpenAI embeddings.
Works identically for local development and Google Cloud production.
Provides persistent vector storage across deployments.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# Configuration
INDEX_NAME = "elena-construction-docs"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Environment variables
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')

# Lazy initialization
pinecone_client = None
openai_client = None


class PineconeVectorStore:
    """Manages vector embeddings and semantic search using Pinecone."""

    def __init__(self):
        global pinecone_client, openai_client

        # Initialize Pinecone client
        if pinecone_client is None:
            if not PINECONE_API_KEY:
                raise ValueError("PINECONE_API_KEY not found in environment")

            print(f"Connecting to Pinecone...")
            pinecone_client = Pinecone(api_key=PINECONE_API_KEY.strip())
            print(f"✓ Connected to Pinecone")

        # Initialize OpenAI client
        if openai_client is None:
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment")
            openai_client = OpenAI(api_key=OPENAI_API_KEY.strip())

        self.pc = pinecone_client
        self._init_index()

    def _init_index(self):
        """Initialize or connect to Pinecone index."""
        print(f"{'='*80}")
        print(f"PINECONE VECTOR STORE INITIALIZATION")
        print(f"{'='*80}")
        print(f"  Environment: {PINECONE_ENVIRONMENT}")

        # Check if index exists
        existing_indexes = [index.name for index in self.pc.list_indexes()]

        if INDEX_NAME not in existing_indexes:
            # Create index
            print(f"  Creating new index: {INDEX_NAME}")
            self.pc.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                )
            )
            print(f"✓ Index created: {INDEX_NAME}")
        else:
            print(f"✓ Using existing index: {INDEX_NAME}")

        # Connect to index
        self.index = self.pc.Index(INDEX_NAME)

        # Get index stats
        stats = self.index.describe_index_stats()
        vector_count = stats.get('total_vector_count', 0)

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
            # Generate deterministic ID from original ID
            chunk_id_str = chunk['id']
            # UUID v5 (SHA-1 namespace-based) - deterministic and unique
            chunk_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id_str))

            # Clean metadata - convert None to empty string and ensure all values are strings
            clean_metadata = {}
            for key, value in chunk['metadata'].items():
                if value is not None:
                    # Pinecone requires metadata values to be strings, numbers, or booleans
                    clean_metadata[key] = str(value) if not isinstance(value, (int, float, bool)) else value
                else:
                    clean_metadata[key] = ""

            # Add original ID and content preview to metadata
            clean_metadata['original_id'] = chunk_id_str
            clean_metadata['content_preview'] = chunk['content'][:500]

            vectors.append({
                'id': chunk_uuid,
                'values': embeddings[i],
                'metadata': clean_metadata
            })

        # Upload in batches
        print(f"\nUploading vectors to Pinecone...")
        uploaded_count = 0

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            batch_num = i // batch_size + 1

            try:
                self.index.upsert(vectors=batch)
                uploaded_count += len(batch)
                print(f"  Batch {batch_num}: Uploaded {i+1}-{min(i+batch_size, len(vectors))} of {len(vectors)}")

            except Exception as e:
                print(f"  ✗ ERROR uploading batch {batch_num}: {type(e).__name__}: {e}")
                raise

        # Verify upload
        stats = self.index.describe_index_stats()
        final_count = stats.get('total_vector_count', 0)

        print(f"\n{'='*80}")
        print(f"UPLOAD SUMMARY:")
        print(f"  Total vectors processed: {uploaded_count}")
        print(f"  Total vectors in index: {final_count}")

        if final_count < len(chunks):
            print(f"\n  ⚠ MISMATCH: Expected {len(chunks)}, got {final_count}")
            print(f"    Missing: {len(chunks) - final_count} vectors")
            print(f"    Note: Pinecone indexing may take a few moments to complete")
        else:
            print(f"  ✓ Upload complete!")

        print(f"{'='*80}\n")

    def search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Semantic search using query embedding.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter: Metadata filter (Pinecone supports rich filtering)

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

        # Format results - restore original IDs from metadata
        formatted_results = []
        for match in results.get('matches', []):
            formatted_results.append({
                'id': match['metadata'].get('original_id', match['id']),
                'score': match['score'],
                'metadata': match['metadata']
            })

        return formatted_results

    def delete_all(self):
        """Delete all vectors from index (for re-indexing)."""
        print(f"Deleting all vectors from index: {INDEX_NAME}")
        self.index.delete(delete_all=True)
        print(f"✓ All vectors deleted")


# Singleton instance
_vector_store = None

def get_vector_store() -> PineconeVectorStore:
    """Get or create PineconeVectorStore singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = PineconeVectorStore()
    return _vector_store
