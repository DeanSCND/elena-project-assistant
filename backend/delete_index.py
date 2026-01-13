#!/usr/bin/env python3
"""Delete Pinecone index to force re-upload."""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
INDEX_NAME = os.getenv('PINECONE_INDEX', 'elena-construction-docs-dev')

pc = Pinecone(api_key=PINECONE_API_KEY)

print(f"Deleting all vectors from index: {INDEX_NAME}")
index = pc.Index(INDEX_NAME)
index.delete(delete_all=True)

print(f"✓ Index cleared. Vector count: {index.describe_index_stats().total_vector_count}")
