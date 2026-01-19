#!/bin/bash

# Enhanced Construction Agent V2 - Direct Startup
# Starts the enhanced agent without prompts

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Enhanced Construction Agent V2${NC}"
echo "=================================================="

# Check for required directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create a .env file with:"
    echo "  OPENAI_API_KEY=your-key-here"
    echo "  ELEVENLABS_API_KEY=your-key-here (optional)"
    exit 1
fi

# Check for OpenAI API key
if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=$" .env; then
    echo -e "${RED}❌ Error: OPENAI_API_KEY not set in .env file!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configured${NC}"

# Backend Setup
echo -e "\n${YELLOW}Setting up backend...${NC}"

cd backend

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry not found. Installing poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install backend dependencies
echo "Installing Python dependencies..."
poetry install

# Set port
PORT=8100

# Frontend Setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"

cd ../frontend

# Check if npm/yarn is installed
if command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
elif command -v yarn &> /dev/null; then
    PKG_MANAGER="yarn"
else
    echo -e "${RED}Neither npm nor yarn found. Please install Node.js${NC}"
    exit 1
fi

# Check if package.json exists, if not create it
if [ ! -f package.json ]; then
    echo "Creating package.json for frontend..."
    cat > package.json << 'EOF'
{
  "name": "construction-agent-frontend",
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

# Install frontend dependencies
echo "Installing frontend dependencies..."
$PKG_MANAGER install

# Create Vite config if not exists
if [ ! -f vite.config.js ]; then
    echo "Creating vite.config.js..."
    cat > vite.config.js << EOF
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:${PORT}',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
EOF
fi

# Start Docker services
echo -e "\n${GREEN}Starting Docker services (Qdrant + Firestore)...${NC}"
cd "$PROJECT_ROOT"

# Check if Qdrant is already running
if docker ps | grep -q qdrant; then
    echo -e "${GREEN}✓ Qdrant already running${NC}"
else
    # Start Qdrant container
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v qdrant_data:/qdrant/storage \
        qdrant/qdrant:latest

    echo "Waiting for Qdrant to be ready..."
    for i in {1..10}; do
        if curl -s http://localhost:6333/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Qdrant is ready!${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
fi

# Check if Firestore is already running
if docker ps | grep -q firestore; then
    echo -e "${GREEN}✓ Firestore already running${NC}"
else
    # Start Firestore emulator
    docker run -d \
        --name firestore-emulator \
        -p 8080:8080 \
        -e FIRESTORE_PROJECT_ID=eleventyseven-45e7c \
        -e PORT=8080 \
        mtlynch/firestore-emulator

    echo "Waiting for Firestore to be ready..."
    for i in {1..10}; do
        if curl -s http://localhost:8080 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Firestore is ready!${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
fi

# Start services
echo -e "\n${GREEN}Starting services...${NC}"
echo "=================================================="

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    echo -e "${YELLOW}Note: Docker containers still running.${NC}"
    echo -e "${YELLOW}Stop with: docker stop qdrant firestore-emulator${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend (Enhanced V2)
echo -e "\n${GREEN}Starting Enhanced Backend V2...${NC}"
cd "$PROJECT_ROOT/backend"
FIRESTORE_EMULATOR_HOST=localhost:8080 PORT=$PORT poetry run python app_v2.py &
BACKEND_PID=$!

# Wait for backend to start and analyze documents (takes longer - 90 docs)
echo "Waiting for backend to initialize and analyze documents..."
for i in {1..60}; do
    if curl -s "http://localhost:${PORT}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start! Check the logs above.${NC}"
    exit 1
fi

# Start frontend (Enhanced V2)
echo -e "\n${GREEN}Starting Enhanced Frontend V2...${NC}"
cd "$PROJECT_ROOT/frontend"
$PKG_MANAGER run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

# Display access information
echo -e "\n${GREEN}=================================================="
echo "🎉 Enhanced Construction Agent V2 is running!"
echo "=================================================="
echo ""
echo "📋 Access the application at:"
echo -e "   ${GREEN}http://localhost:5173${NC}"
echo ""
echo "🔧 Backend API:"
echo -e "   ${GREEN}http://localhost:${PORT}${NC}"
echo ""
echo "📊 Check health status:"
echo -e "   ${GREEN}http://localhost:${PORT}/health${NC}"
echo ""
echo "🧠 Features:"
echo "  • Deep document analysis at startup"
echo "  • Multi-step reasoning with transparency"
echo "  • Pattern recognition & base component identification"
echo "  • Voice interaction support"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================================="

# Keep script running
wait