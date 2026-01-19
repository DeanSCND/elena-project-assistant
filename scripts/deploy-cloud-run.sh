#!/bin/bash

# Elena Construction Agent - Cloud Run Deployment Script
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="eleventyseven-45e7c"
REGION="us-central1"
BACKEND_SERVICE="elena-agent"

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 Elena Agent - Cloud Run Deployment            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# =============================================================================
# Step 1: Build and Deploy Backend using Cloud Build
# =============================================================================

echo -e "\n${BLUE}[1/2] Building and deploying Elena Agent backend...${NC}"
echo -e "${BLUE}Using Pinecone (managed vector database)...${NC}"

# Trigger Cloud Build (uses cloudbuild.yaml)
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=$PROJECT_ID \
  .

# Get backend service URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
  --platform=managed \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)')

echo -e "${GREEN}✓ Backend deployed at: $BACKEND_URL${NC}"

# =============================================================================
# Step 2: Display deployment information
# =============================================================================

echo -e "\n${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        🎉 Deployment Complete!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📱 Application URL:${NC}"
echo -e "   ${GREEN}→ $BACKEND_URL${NC}"
echo ""
echo -e "${BLUE}🔧 Services:${NC}"
echo -e "   Backend:  $BACKEND_URL"
echo -e "   Vector DB: Pinecone (managed service)"
echo ""
echo -e "${BLUE}📊 Health Check:${NC}"
echo -e "   ${YELLOW}curl $BACKEND_URL/health${NC}"
echo ""
echo -e "${BLUE}🔍 View Logs:${NC}"
echo -e "   ${YELLOW}gcloud run services logs tail $BACKEND_SERVICE --project=$PROJECT_ID${NC}"
echo ""
echo -e "${BLUE}📝 Manage Services:${NC}"
echo -e "   ${YELLOW}https://console.cloud.google.com/run?project=$PROJECT_ID${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
