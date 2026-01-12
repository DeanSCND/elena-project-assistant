#!/bin/bash

# Construction Agent POC - Complete Startup Script with Frontend Server
# This script handles environment setup, dependency installation, and launches both backend and frontend servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}🏗️  Construction Agent POC - Full Stack Startup${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"

    # Kill backend server
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi

    # Kill frontend server
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    # Kill any remaining node processes on port 5173
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true

    # Kill any remaining python processes on backend port
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true

    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# 1. Check Python version
echo -e "${BLUE}Step 1: Checking Python installation...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python3 not found. Please install Python 3.11 or higher"
    exit 1
fi

# 2. Check Node.js
echo -e "\n${BLUE}Step 2: Checking Node.js installation...${NC}"
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 18 or higher"
    echo "  Install from: https://nodejs.org/"
    exit 1
fi

# 3. Check/Install Poetry
echo -e "\n${BLUE}Step 3: Checking Poetry installation...${NC}"
if command_exists poetry; then
    POETRY_VERSION=$(poetry --version | cut -d' ' -f3)
    print_status "Poetry $POETRY_VERSION found"
else
    print_warning "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"

    if command_exists poetry; then
        print_status "Poetry installed successfully"
    else
        print_error "Failed to install Poetry"
        exit 1
    fi
fi

# 4. Check for .env file
echo -e "\n${BLUE}Step 4: Checking environment configuration...${NC}"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    print_status ".env file found"

    # Check if OPENAI_API_KEY is set
    if grep -q "^OPENAI_API_KEY=sk-" "$ENV_FILE"; then
        print_status "OpenAI API key configured"
    else
        print_warning "OpenAI API key not found or invalid in .env"
        read -p "Would you like to add it now? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter your OpenAI API key: " API_KEY
            echo "OPENAI_API_KEY=$API_KEY" >> "$ENV_FILE"
            print_status "API key added to .env"
        fi
    fi
else
    print_warning ".env file not found. Creating from template..."
    cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
    print_status ".env file created"

    read -p "Enter your OpenAI API key: " API_KEY
    sed -i.bak "s/sk-your-openai-api-key-here/$API_KEY/" "$ENV_FILE"
    rm "${ENV_FILE}.bak" 2>/dev/null || true
    print_status "API key added to .env"
fi

# 5. Check Aurora documents
echo -e "\n${BLUE}Step 5: Checking Aurora project documents...${NC}"
AURORA_DIR="$PROJECT_ROOT/../Aurora (Safeway) Regina, SK"

if [ -d "$AURORA_DIR" ]; then
    AI_FILES=$(find "$AURORA_DIR" -name "*.AI.md" 2>/dev/null | wc -l | tr -d ' ')
    print_status "Aurora project folder found ($AI_FILES AI analysis files)"
else
    print_error "Aurora project folder not found"
    exit 1
fi

# 6. Install Backend dependencies
echo -e "\n${BLUE}Step 6: Installing backend dependencies...${NC}"
cd "$BACKEND_DIR"
poetry install --no-interaction --quiet

if [ $? -eq 0 ]; then
    print_status "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi

# 7. Install Frontend dependencies
echo -e "\n${BLUE}Step 7: Installing frontend dependencies...${NC}"
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -eq 0 ]; then
        print_status "Frontend dependencies installed"
    else
        print_error "Failed to install frontend dependencies"
        exit 1
    fi
else
    print_status "Frontend dependencies already installed"
fi

# 8. Check ports
echo -e "\n${BLUE}Step 8: Checking port availability...${NC}"

# Backend port
BACKEND_PORT=8100
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Backend port $BACKEND_PORT is in use"
    read -p "Kill process and continue? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
        print_status "Cleared backend port $BACKEND_PORT"
    else
        read -p "Enter alternative backend port: " BACKEND_PORT
    fi
else
    print_status "Backend port $BACKEND_PORT is available"
fi

# Frontend port
FRONTEND_PORT=5173
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Frontend port $FRONTEND_PORT is in use"
    read -p "Kill process and continue? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
        print_status "Cleared frontend port $FRONTEND_PORT"
    else
        print_error "Frontend needs port 5173 for Vite"
        exit 1
    fi
else
    print_status "Frontend port $FRONTEND_PORT is available"
fi

# 9. Update frontend config if backend port changed
if [ "$BACKEND_PORT" != "8100" ]; then
    echo -e "\n${BLUE}Updating frontend configuration...${NC}"

    # Update vite.config.js proxy
    VITE_CONFIG="$FRONTEND_DIR/vite.config.js"
    sed -i.bak "s|target: 'http://localhost:[0-9]*'|target: 'http://localhost:$BACKEND_PORT'|g" "$VITE_CONFIG"
    rm "${VITE_CONFIG}.bak" 2>/dev/null || true

    # Update app.js fallback
    APP_JS="$FRONTEND_DIR/app.js"
    sed -i.bak "s|'http://localhost:[0-9]*'|'http://localhost:$BACKEND_PORT'|g" "$APP_JS"
    rm "${APP_JS}.bak" 2>/dev/null || true

    print_status "Updated frontend to use backend port $BACKEND_PORT"
fi

# 10. Start Backend Server
echo -e "\n${BLUE}Step 9: Starting backend server...${NC}"
echo "========================================="

cd "$BACKEND_DIR"
poetry run uvicorn app:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..10}; do
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
        print_status "Backend server running on port $BACKEND_PORT"
        break
    fi
    sleep 1
done

# 11. Start Frontend Server
echo -e "\n${BLUE}Step 10: Starting frontend server...${NC}"
echo "========================================="

cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 3

if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_status "Frontend server running on port $FRONTEND_PORT"
else
    print_warning "Frontend might still be starting..."
fi

# Final message
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Construction Agent POC is fully running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "🖥️  Frontend: http://localhost:$FRONTEND_PORT"
echo "🔧 Backend API: http://localhost:$BACKEND_PORT"
echo ""
echo "The browser should open automatically."
echo "If not, navigate to: http://localhost:$FRONTEND_PORT"
echo ""
echo "Example queries:"
echo "  • What's the ceiling height in meat prep?"
echo "  • Is there a conflict between trellis and HVAC?"
echo "  • What are the grid dimensions?"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Keep script running
wait