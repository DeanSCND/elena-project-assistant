#!/bin/bash

# Elena Construction Agent - Comprehensive Startup Script
# Starts all components: Backend, Frontend, and optionally Firestore

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8100
FRONTEND_PORT=5174
FIRESTORE_PORT=8080
QDRANT_PORT=6333

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 Elena Construction Agent - Startup Manager    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"

# Get script and project directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# =============================================================================
# Helper Functions
# =============================================================================

check_port() {
    local port=$1
    lsof -ti:$port > /dev/null 2>&1
}

kill_port() {
    local port=$1
    local service=$2
    if check_port $port; then
        echo -e "${YELLOW}⚠️  Port $port is already in use by $service${NC}"
        echo -e "${YELLOW}   Killing existing process...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}   ✓ Process killed${NC}"
    fi
}

wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=${3:-30}  # Default 30, but can override

    echo "Waiting for $name to be ready..."
    for i in $(seq 1 $max_attempts); do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name is ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo -e "${RED}✗ $name failed to start after ${max_attempts}s${NC}"
    return 1
}

# =============================================================================
# Environment Checks
# =============================================================================

echo -e "\n${BLUE}[1/6] Checking environment...${NC}"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create a .env file with required API keys"
    exit 1
fi

# Check for OpenAI API key
if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=$" .env; then
    echo -e "${RED}❌ Error: OPENAI_API_KEY not set in .env file!${NC}"
    exit 1
fi

# Check for Pinecone API key
if ! grep -q "PINECONE_API_KEY=" .env || grep -q "PINECONE_API_KEY=$" .env; then
    echo -e "${YELLOW}⚠️  Warning: PINECONE_API_KEY not set. Vector search will fail.${NC}"
fi

echo -e "${GREEN}✓ Environment variables configured${NC}"

# =============================================================================
# Cleanup Existing Processes
# =============================================================================

echo -e "\n${BLUE}[2/6] Cleaning up existing processes...${NC}"

kill_port $BACKEND_PORT "backend"
kill_port $FRONTEND_PORT "frontend"
kill_port $QDRANT_PORT "qdrant"

echo -e "${GREEN}✓ Ports cleared${NC}"

# =============================================================================
# Backend Setup
# =============================================================================

echo -e "\n${BLUE}[3/6] Setting up backend...${NC}"

cd backend

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Poetry not found. Installing poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install backend dependencies
echo "Installing Python dependencies..."
# Check if lock file needs updating
if ! poetry check --lock 2>&1 | grep -q "All set!"; then
    echo "Updating poetry lock file..."
    poetry lock
fi
poetry install --quiet

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# =============================================================================
# Frontend Setup
# =============================================================================

echo -e "\n${BLUE}[4/6] Setting up frontend...${NC}"

cd ../frontend

# Determine package manager
if command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
elif command -v yarn &> /dev/null; then
    PKG_MANAGER="yarn"
else
    echo -e "${RED}Neither npm nor yarn found. Please install Node.js${NC}"
    exit 1
fi

# Check for package.json
if [ ! -f package.json ]; then
    echo -e "${YELLOW}Creating package.json...${NC}"
    cat > package.json << 'EOF'
{
  "name": "elena-construction-agent",
  "version": "2.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}
EOF
fi

# Check for vite.config.js
if [ ! -f vite.config.js ]; then
    echo -e "${YELLOW}Creating vite.config.js...${NC}"
    cat > vite.config.js << EOF
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: $FRONTEND_PORT,
    open: true
  }
})
EOF
fi

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    $PKG_MANAGER install
else
    echo "Frontend dependencies already installed"
fi

echo -e "${GREEN}✓ Frontend ready${NC}"

# =============================================================================
# Optional: Firestore Emulator
# =============================================================================

echo -e "\n${BLUE}[5/6] Starting Docker services (Required)...${NC}"

cd "$PROJECT_ROOT"

# Check if Docker is running, wait if starting up
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Docker daemon not responding. Checking if Docker Desktop is installed...${NC}"

    # Try to start Docker Desktop if it exists
    if [ -d "/Applications/Docker.app" ]; then
        echo "Starting Docker Desktop..."
        open -a Docker

        echo "Waiting for Docker daemon to be ready..."
        max_wait=60
        elapsed=0
        while ! docker info > /dev/null 2>&1; do
            if [ $elapsed -ge $max_wait ]; then
                echo -e "${RED}❌ Docker failed to start after ${max_wait}s${NC}"
                echo -e "${YELLOW}   Please start Docker Desktop manually and run this script again.${NC}"
                exit 1
            fi
            echo -n "."
            sleep 2
            elapsed=$((elapsed + 2))
        done
        echo -e "\n${GREEN}✓ Docker is ready${NC}"
    else
        echo -e "${RED}❌ Docker Desktop not found at /Applications/Docker.app${NC}"
        echo -e "${YELLOW}   Please install Docker Desktop and run this script again.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
fi

if [ ! -f docker-compose.yml ]; then
    echo -e "${RED}❌ docker-compose.yml not found!${NC}"
    exit 1
fi

echo "Starting Firestore emulator and Qdrant..."
docker-compose up -d

# Wait for services
wait_for_service "http://localhost:$FIRESTORE_PORT" "Firestore emulator" || {
    echo -e "${RED}Firestore failed to start${NC}"
    exit 1
}

wait_for_service "http://localhost:$QDRANT_PORT/collections" "Qdrant" || {
    echo -e "${RED}Qdrant failed to start${NC}"
    exit 1
}

echo -e "${GREEN}✓ Docker services started${NC}"

# =============================================================================
# Start Services
# =============================================================================

echo -e "\n${BLUE}[6/6] Starting services...${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"

    # Kill background jobs
    jobs -p | xargs -r kill 2>/dev/null || true

    # Kill ports directly
    lsof -ti:$BACKEND_PORT | xargs -r kill -9 2>/dev/null || true
    lsof -ti:$FRONTEND_PORT | xargs -r kill -9 2>/dev/null || true

    echo -e "${GREEN}✓ Services stopped${NC}"
    echo -e "${YELLOW}Note: Firestore emulator may still be running. Stop with: docker-compose down${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo -e "\n${GREEN}Starting Backend (Elena AI)...${NC}"
cd "$PROJECT_ROOT/backend"
FIRESTORE_EMULATOR_HOST=localhost:$FIRESTORE_PORT PORT=$BACKEND_PORT poetry run python app_v2.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready (longer timeout - loading documents takes time)
wait_for_service "http://localhost:${BACKEND_PORT}/health" "Backend API" 90 || {
    echo -e "${RED}Backend failed to start. Check logs/backend.log${NC}"
    exit 1
}

# Start frontend
echo -e "\n${GREEN}Starting Frontend (UI)...${NC}"
cd "$PROJECT_ROOT/frontend"
$PKG_MANAGER run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend
sleep 3

# Check if services are running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend process died. Check logs/backend.log${NC}"
    exit 1
fi

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}Frontend process died. Check logs/frontend.log${NC}"
    exit 1
fi

# =============================================================================
# Display Access Information
# =============================================================================

echo -e "\n${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        🎉 Elena is Ready!                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📱 Web Interface:${NC}"
echo -e "   ${GREEN}→ http://localhost:$FRONTEND_PORT${NC}"
echo ""
echo -e "${BLUE}🔧 Backend API:${NC}"
echo -e "   ${GREEN}→ http://localhost:$BACKEND_PORT${NC}"
echo -e "   ${GREEN}→ http://localhost:$BACKEND_PORT/health${NC} (health check)"
echo -e "   ${GREEN}→ http://localhost:$BACKEND_PORT/knowledge${NC} (knowledge base)"
echo ""

if docker ps | grep -q firestore; then
    echo -e "${BLUE}💾 Firestore Emulator:${NC}"
    echo -e "   ${GREEN}→ http://localhost:$FIRESTORE_PORT${NC}"
    echo ""
fi

echo -e "${BLUE}📊 Process IDs:${NC}"
echo -e "   Backend:  $BACKEND_PID"
echo -e "   Frontend: $FRONTEND_PID"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   ${YELLOW}tail -f logs/backend.log${NC}"
echo -e "   ${YELLOW}tail -f logs/frontend.log${NC}"
echo ""
echo -e "${BLUE}🛑 Stop Services:${NC}"
echo -e "   ${YELLOW}Press Ctrl+C${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"

# Keep script running
wait
