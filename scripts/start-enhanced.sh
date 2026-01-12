#!/bin/bash

# Enhanced Construction Agent Startup Script
# Starts the V2 agent with deep reasoning capabilities

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

# Ask which backend version to run
echo -e "\n${YELLOW}Which backend version would you like to run?${NC}"
echo "1) Original simple agent (app.py)"
echo "2) Enhanced V2 with reasoning (app_v2.py)"
echo -n "Enter choice (1-2): "
read backend_choice

case $backend_choice in
    1)
        BACKEND_FILE="app.py"
        BACKEND_NAME="Simple Agent"
        ;;
    2)
        BACKEND_FILE="app_v2.py"
        BACKEND_NAME="Enhanced Agent V2"
        ;;
    *)
        echo -e "${RED}Invalid choice. Using Enhanced V2 by default.${NC}"
        BACKEND_FILE="app_v2.py"
        BACKEND_NAME="Enhanced Agent V2"
        ;;
esac

# Ask for port
echo -n "Enter port for backend (default: 8100): "
read port
PORT=${port:-8100}

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

# Ask which frontend version to use
echo -e "\n${YELLOW}Which frontend version would you like to run?${NC}"
echo "1) Original simple UI (index.html)"
echo "2) Enhanced V2 with reasoning display (index_v2.html)"
echo -n "Enter choice (1-2): "
read frontend_choice

case $frontend_choice in
    1)
        FRONTEND_FILE="index.html"
        FRONTEND_NAME="Simple UI"
        ;;
    2)
        FRONTEND_FILE="index_v2.html"
        FRONTEND_NAME="Enhanced UI V2"
        ;;
    *)
        echo -e "${RED}Invalid choice. Using Enhanced V2 by default.${NC}"
        FRONTEND_FILE="index_v2.html"
        FRONTEND_NAME="Enhanced UI V2"
        ;;
esac

# Create index.html symlink for Vite
if [ -f "$FRONTEND_FILE" ]; then
    ln -sf "$FRONTEND_FILE" index.html
    echo -e "${GREEN}✓ Using $FRONTEND_NAME${NC}"
fi

# Start services
echo -e "\n${GREEN}Starting services...${NC}"
echo "=================================================="
echo -e "Backend: ${BACKEND_NAME} on port ${PORT}"
echo -e "Frontend: ${FRONTEND_NAME} on port 5173"
echo "=================================================="

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo -e "\n${GREEN}Starting backend (${BACKEND_NAME})...${NC}"
cd ../backend
PORT=$PORT poetry run python "$BACKEND_FILE" &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start! Check the logs above.${NC}"
    exit 1
fi

# Start frontend
echo -e "\n${GREEN}Starting frontend (${FRONTEND_NAME})...${NC}"
cd ../frontend
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
echo "  • Deep document analysis"
echo "  • Multi-step reasoning"
echo "  • Pattern recognition"
echo "  • Base component identification"
echo "  • Voice interaction"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================================="

# Keep script running
wait