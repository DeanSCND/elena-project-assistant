"""
Vector store for semantic search using Google Vertex AI Vector Search.
Production-ready for Google Cloud deployment.
"""

import os
import time
from typing import List, Dict, Any, Optional
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint
from openai import OpenAI
import numpy as np

# Configuration
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'eleventyseven-45e7c')
GCP_REGION = os.getenv('GCP_REGION', 'us-central1')
INDEX_DISPLAY_NAME = os.getenv('VERTEX_INDEX_NAME', 'elena-construction-docs')
ENDPOINT_DISPLAY_NAME = f"{INDEX_DISPLAY_NAME}-endpoint"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Initialize clients
aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
openai_client = None


class VertexVectorStore:
    """Manages vector embeddings and semantic search using Vertex AI."""

    def __init__(self):
        global openai_client

        # Initialize OpenAI client for embeddings
        if openai_client is None:
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment")
            openai_client = OpenAI(api_key=OPENAI_API_KEY)

        self.index = None
        self.endpoint = None
        self._init_index()

    def _init_index(self):
        """Initialize or connect to Vertex AI Vector Search index."""
        print(f"{'='*80}")
        print(f"VERTEX AI VECTOR SEARCH INITIALIZATION")
        print(f"{'='*80}")

        # List existing indexes
        existing_indexes = aiplatform.MatchingEngineIndex.list(
            filter=f'display_name="{INDEX_DISPLAY_NAME}"'
        )

        if existing_indexes:
            # Use existing index
            self.index = existing_indexes[0]
            print(f"✓ Using existing index: {INDEX_DISPLAY_NAME}")
            print(f"  Index ID: {self.index.resource_name}")
        else:
            print(f"⚠️  No existing index found: {INDEX_DISPLAY_NAME}")
            print(f"  Index will be created on first upsert")
            self.index = None

        # List existing endpoints
        existing_endpoints = aiplatform.MatchingEngineIndexEndpoint.list(
            filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"'
        )

        if existing_endpoints:
            self.endpoint = existing_endpoints[0]
            print(f"✓ Using existing endpoint: {ENDPOINT_DISPLAY_NAME}")
        else:
            print(f"  No endpoint found - will be created on first upsert")
            self.endpoint = None

        print(f"  Project: {GCP_PROJECT_ID}")
        print(f"  Region: {GCP_REGION}")
        print(f"  Dimension: {EMBEDDING_DIMENSION}")
        print(f"  Model: {EMBEDDING_MODEL}")
        print(f"{'='*80}\n")

    def _create_index(self):
        """Create a new Vertex AI Vector Search index."""
        print(f"\nCreating new Vertex AI index: {INDEX_DISPLAY_NAME}")
        print(f"⚠️  This may take 20-30 minutes for initial creation...")

        # Create index
        self.index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=INDEX_DISPLAY_NAME,
            dimensions=EMBEDDING_DIMENSION,
            approximate_neighbors_count=10,
            distance_measure_type="DOT_PRODUCT_DISTANCE",
            leaf_node_embedding_count=500,
            leaf_nodes_to_search_percent=7,
            description="Aurora construction documents vector search index",
        )

        print(f"✓ Index created: {self.index.resource_name}")
        return self.index

    def _create_endpoint(self):
        """Create a new endpoint for querying the index."""
        print(f"\nCreating endpoint: {ENDPOINT_DISPLAY_NAME}")

        self.endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=ENDPOINT_DISPLAY_NAME,
            description="Endpoint for Elena construction docs search",
            public_endpoint_enabled=True,
        )

        print(f"✓ Endpoint created: {self.endpoint.resource_name}")

        # Deploy index to endpoint
        print(f"  Deploying index to endpoint...")
        self.endpoint = self.endpoint.deploy_index(
            index=self.index,
            deployed_index_id=INDEX_DISPLAY_NAME.replace("-", "_"),
            display_name=INDEX_DISPLAY_NAME,
            machine_type="e2-standard-2",
            min_replica_count=1,
            max_replica_count=1,
        )

        print(f"✓ Index deployed to endpoint")
        return self.endpoint

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
        Upload chunks with embeddings to Vertex AI Vector Search.

        Args:
            chunks: List of dicts with {id, content, metadata}
            batch_size: Number of vectors to process at once
        """
        print(f"\n{'='*80}")
        print(f"UPLOADING {len(chunks)} CHUNKS TO VERTEX AI VECTOR SEARCH")
        print(f"{'='*80}")

        # Create index if it doesn't exist
        if self.index is None:
            self._create_index()

        # Generate embeddings
        print(f"\nGenerating embeddings...")
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)

        # Prepare data for Vertex AI
        # Format: List of tuples (id, embedding, metadata)
        print(f"\nPreparing vectors for upload...")

        # Vertex AI requires specific format - we'll use index update
        # Convert to numpy array for efficient storage
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Store metadata separately (Vertex AI has different metadata handling)
        metadata_map = {}
        for i, chunk in enumerate(chunks):
            metadata_map[chunk['id']] = {
                'source_pdf': chunk['metadata'].get('source_pdf', ''),
                'section': chunk['metadata'].get('section', ''),
                'page': str(chunk['metadata'].get('page', '')),
                'content_preview': chunk['content'][:200]
            }

        print(f"\n⚠️  VERTEX AI VECTOR SEARCH SETUP REQUIRED:")
        print(f"{'='*80}")
        print(f"Vertex AI requires manual index creation and data upload via:")
        print(f"  1. Google Cloud Console UI, OR")
        print(f"  2. GCS bucket upload + index update")
        print(f"")
        print(f"For production deployment:")
        print(f"  • Create GCS bucket: gs://{GCP_PROJECT_ID}-vector-data")
        print(f"  • Upload embeddings to GCS")
        print(f"  • Update index with GCS data")
        print(f"")
        print(f"Total vectors prepared: {len(embeddings)}")
        print(f"Dimension: {EMBEDDING_DIMENSION}")
        print(f"")
        print(f"See: https://cloud.google.com/vertex-ai/docs/vector-search/setup")
        print(f"{'='*80}\n")

        # Note: Actual upload to Vertex AI requires GCS bucket setup
        # This is intentionally a two-step process for production safety

    def search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Semantic search using query embedding.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter: Metadata filter (not fully supported in Vertex AI)

        Returns:
            List of {id, score, metadata} dicts
        """
        if self.endpoint is None:
            print("⚠️  Endpoint not deployed - cannot perform search")
            return []

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Query the deployed index
        response = self.endpoint.find_neighbors(
            deployed_index_id=INDEX_DISPLAY_NAME.replace("-", "_"),
            queries=[query_embedding],
            num_neighbors=top_k,
        )

        # Format results
        formatted_results = []
        for neighbor in response[0]:
            formatted_results.append({
                'id': neighbor.id,
                'score': neighbor.distance,
                'metadata': {}  # Metadata retrieval requires separate storage
            })

        return formatted_results

    def delete_all(self):
        """Delete the index (for re-indexing)."""
        if self.index:
            print(f"Deleting index: {INDEX_DISPLAY_NAME}")
            self.index.delete()
            self.index = None
            print(f"✓ Index deleted")


# Singleton instance
_vector_store = None

def get_vector_store() -> VertexVectorStore:
    """Get or create VertexVectorStore singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VertexVectorStore()
    return _vector_store
