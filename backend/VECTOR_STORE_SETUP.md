# Vector Store Setup Guide

Elena uses different vector databases for local development vs Google Cloud production.

## Architecture: Separation of Concerns

```
Local Development  →  Pinecone (free tier, 2GB limit)
Google Cloud Prod  →  Vertex AI Vector Search (fully managed, unlimited)
```

## Local Development (Pinecone)

### Configuration
In `.env`:
```bash
VECTOR_STORE=pinecone
PINECONE_API_KEY=your-key-here
PINECONE_INDEX=elena-construction-docs-dev
```

### Limitations
- Free tier: 2GB storage (~2,600 vectors at 1536 dimensions)
- Good for testing with subset of documents
- No persistence across deployments

## Google Cloud Production (Vertex AI)

### Configuration
In `.env` (or Dockerfile):
```bash
VECTOR_STORE=vertex
GCP_PROJECT_ID=eleventyseven-45e7c
GCP_REGION=us-central1
VERTEX_INDEX_NAME=elena-construction-docs
```

### Setup Steps

#### 1. Enable Vertex AI API
```bash
gcloud services enable aiplatform.googleapis.com --project=eleventyseven-45e7c
```

#### 2. Create Vector Search Index

The index will be created automatically on first run, but manual creation is recommended for production:

```bash
# Via gcloud CLI (recommended for automation)
gcloud ai indexes create \
  --display-name=elena-construction-docs \
  --description="Aurora construction documents vector search" \
  --region=us-central1 \
  --index-update-method=stream \
  --dimensions=1536 \
  --shard-size=SHARD_SIZE_SMALL
```

Or use the Google Cloud Console:
1. Go to Vertex AI → Vector Search
2. Click "Create Index"
3. Choose:
   - Name: `elena-construction-docs`
   - Dimensions: 1536
   - Distance: DOT_PRODUCT
   - Algorithm: Tree-AH (for efficiency)

#### 3. Deploy Index to Endpoint

```bash
# Create endpoint
gcloud ai index-endpoints create \
  --display-name=elena-construction-docs-endpoint \
  --region=us-central1 \
  --public-endpoint-enabled

# Deploy index to endpoint (takes ~20 minutes)
gcloud ai index-endpoints deploy-index ENDPOINT_ID \
  --deployed-index-id=elena_docs \
  --index=INDEX_ID \
  --region=us-central1
```

#### 4. Upload Vectors

The app will automatically generate embeddings and attempt to upload. However, Vertex AI requires a two-step process for production safety:

1. **Automatic embedding generation**: App generates OpenAI embeddings
2. **Manual upload**: Follow on-screen instructions to upload via GCS bucket

**Alternative: Programmatic Upload**

For full automation, modify `vector_store_vertex.py` to use the Vertex AI batch upload API with GCS buckets.

### Production Benefits

✅ **No storage limits** - Handle millions of vectors
✅ **Auto-scaling** - Scales to zero when not in use
✅ **Managed by Google** - No infrastructure maintenance
✅ **Native Cloud Run integration** - Same project, same IAM
✅ **Production SLA** - Enterprise reliability
✅ **Cost-effective** - Pay per query (~$5/month for your scale)

### Costs

- **Index hosting**: ~$0.50/hour per shard (1 shard for <10M vectors)
- **Queries**: $0.000004 per query
- **Embedding storage**: Negligible for 5K vectors

**Estimated monthly cost**: $5-15 for always-on deployment

## Switching Between Environments

### Local Dev → Cloud
1. Set `VECTOR_STORE=vertex` in `.env`
2. Restart app
3. App will use Vertex AI

### Cloud → Local Dev
1. Set `VECTOR_STORE=pinecone` in `.env`
2. Restart app
3. App will use Pinecone (limited to 2,600 vectors)

## Code Structure

```
vector_store_factory.py    # Environment detection & routing
vector_store.py            # Pinecone implementation (local)
vector_store_vertex.py     # Vertex AI implementation (cloud)
app_v2.py                  # Uses factory to get correct store
```

## Troubleshooting

### "Vector count mismatch" (Pinecone)
- Free tier hit 2GB limit
- Only first 2,600 vectors uploaded
- Solution: Switch to Vertex AI or reduce chunk count

### "Endpoint not deployed" (Vertex AI)
- Index created but not deployed to endpoint
- Run deployment command above
- Wait 20-30 minutes for deployment

### "Permission denied" (Vertex AI)
- Enable Vertex AI API
- Check service account has `aiplatform.user` role
- For Cloud Run: use default compute service account

## Next Steps for Production

1. ✅ Enable Vertex AI API
2. ✅ Create index via Console or gcloud
3. ✅ Deploy to endpoint
4. ✅ Set `VECTOR_STORE=vertex` in Dockerfile
5. ✅ Deploy to Cloud Run
6. ✅ Upload all 5,378 vectors (no limits!)

## References

- [Vertex AI Vector Search Docs](https://cloud.google.com/vertex-ai/docs/vector-search/overview)
- [Vertex AI Quickstart](https://cloud.google.com/vertex-ai/docs/vector-search/quickstart)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
