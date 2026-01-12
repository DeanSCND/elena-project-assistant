#!/bin/bash

# Construction Agent POC - Complete Startup Script
# This script handles environment setup, dependency installation, and app launch

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

echo -e "${BLUE}🏗️  Construction Agent POC - Startup Script${NC}"
echo -e "${BLUE}===========================================${NC}\n"

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

# 1. Check Python version
echo -e "${BLUE}Step 1: Checking Python installation...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python $PYTHON_VERSION found"

    # Check if Python 3.11+ as specified in pyproject.toml
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        print_status "Python version meets requirements (3.11+)"
    else
        print_warning "Python 3.11+ recommended, you have $PYTHON_VERSION"
    fi
else
    print_error "Python3 not found. Please install Python 3.11 or higher"
    exit 1
fi

# 2. Check/Install Poetry
echo -e "\n${BLUE}Step 2: Checking Poetry installation...${NC}"
if command_exists poetry; then
    POETRY_VERSION=$(poetry --version | cut -d' ' -f3)
    print_status "Poetry $POETRY_VERSION found"
else
    print_warning "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -

    # Add Poetry to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    if command_exists poetry; then
        print_status "Poetry installed successfully"
    else
        print_error "Failed to install Poetry. Please install manually:"
        echo "  curl -sSL https://install.python-poetry.org | python3 -"
        exit 1
    fi
fi

# 3. Check for .env file
echo -e "\n${BLUE}Step 3: Checking environment configuration...${NC}"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    print_status ".env file found"

    # Check if OPENAI_API_KEY is set
    if grep -q "^OPENAI_API_KEY=sk-" "$ENV_FILE"; then
        print_status "OpenAI API key configured"
    else
        print_warning "OpenAI API key not found or invalid in .env"
        echo ""
        echo "Please add your OpenAI API key to .env file:"
        echo "  OPENAI_API_KEY=sk-your-key-here"
        echo ""
        read -p "Would you like to add it now? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter your OpenAI API key: " API_KEY
            echo "OPENAI_API_KEY=$API_KEY" >> "$ENV_FILE"
            print_status "API key added to .env"
        else
            print_warning "Continuing without API key (chat won't work)"
        fi
    fi
else
    print_warning ".env file not found. Creating from template..."
    cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
    print_status ".env file created from template"

    echo ""
    echo "Please add your OpenAI API key to .env file:"
    echo "  OPENAI_API_KEY=sk-your-key-here"
    echo ""
    read -p "Would you like to add it now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " API_KEY
        sed -i.bak "s/sk-your-openai-api-key-here/$API_KEY/" "$ENV_FILE"
        rm "${ENV_FILE}.bak" 2>/dev/null || true
        print_status "API key added to .env"
    else
        print_warning "Continuing without API key (chat won't work)"
    fi
fi

# 4. Check Aurora documents
echo -e "\n${BLUE}Step 4: Checking Aurora project documents...${NC}"
AURORA_DIR="$PROJECT_ROOT/../Aurora (Safeway) Regina, SK"

if [ -d "$AURORA_DIR" ]; then
    # Count .AI.md files
    AI_FILES=$(find "$AURORA_DIR" -name "*.AI.md" 2>/dev/null | wc -l | tr -d ' ')
    MD_FILES=$(find "$AURORA_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

    print_status "Aurora project folder found"
    print_status "Found $AI_FILES AI analysis files"
    print_status "Found $MD_FILES total markdown files"
else
    print_error "Aurora project folder not found at:"
    echo "  $AURORA_DIR"
    echo ""
    echo "The agent needs the Aurora documents to function."
    echo "Please ensure the Aurora folder exists in the parent directory."
    exit 1
fi

# 5. Install Python dependencies
echo -e "\n${BLUE}Step 5: Installing Python dependencies with Poetry...${NC}"
cd "$BACKEND_DIR"

# Install dependencies
poetry install --no-interaction --quiet

if [ $? -eq 0 ]; then
    print_status "Python dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# 6. Check if port is available
echo -e "\n${BLUE}Step 6: Checking port availability...${NC}"

# Default to port 8100 to avoid conflicts with common services
DEFAULT_PORT=8100
PORT=$DEFAULT_PORT

# Check if default port is available
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port $PORT is already in use"
    echo ""
    echo "Options:"
    echo "  1. Kill the existing process"
    echo "  2. Use a different port"
    echo "  3. Cancel"
    read -p "Choose (1/2/3): " CHOICE
    echo ""

    case $CHOICE in
        1)
            PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
            kill $PID 2>/dev/null || true
            sleep 1
            print_status "Killed process on port $PORT"
            ;;
        2)
            read -p "Enter port number (e.g., 8101): " NEW_PORT
            PORT=$NEW_PORT
            print_status "Will use port $PORT"
            ;;
        *)
            echo "Cancelled"
            exit 0
            ;;
    esac
else
    print_status "Port $PORT is available"
fi

# 7. Start the backend server
echo -e "\n${BLUE}Step 7: Starting the backend server...${NC}"
echo "========================================="
echo ""

# Update frontend to use the correct port
FRONTEND_APP_JS="$FRONTEND_DIR/app.js"
if [ -f "$FRONTEND_APP_JS" ]; then
    # Backup original
    cp "$FRONTEND_APP_JS" "$FRONTEND_APP_JS.bak" 2>/dev/null || true

    # Update the API_BASE URL in the frontend
    sed -i.tmp "s|const API_BASE = 'http://localhost:[0-9]*'|const API_BASE = 'http://localhost:$PORT'|g" "$FRONTEND_APP_JS"
    rm "$FRONTEND_APP_JS.tmp" 2>/dev/null || true
    print_status "Updated frontend to use port $PORT"
fi

echo "Starting server on port $PORT..."
cd "$BACKEND_DIR"
poetry run uvicorn app:app --reload --host 0.0.0.0 --port "$PORT" &
SERVER_URL="http://localhost:$PORT"

SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 3

# Check if server is running
if curl -s "$SERVER_URL/health" > /dev/null 2>&1; then
    print_status "Backend server is running"
else
    print_warning "Server might still be starting..."
fi

# 8. Open the frontend
echo -e "\n${BLUE}Step 8: Opening the chat interface...${NC}"
echo "========================================="

# Determine the OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$FRONTEND_DIR/index.html"
    print_status "Opened chat interface in browser"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command_exists xdg-open; then
        xdg-open "$FRONTEND_DIR/index.html"
        print_status "Opened chat interface in browser"
    else
        print_warning "Please open manually: $FRONTEND_DIR/index.html"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start "$FRONTEND_DIR/index.html"
    print_status "Opened chat interface in browser"
else
    print_warning "Please open manually: $FRONTEND_DIR/index.html"
fi

# Final instructions
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Construction Agent POC is running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 Backend API: $SERVER_URL"
echo "💬 Chat Interface: file://$FRONTEND_DIR/index.html"
echo ""
echo "Example queries to try:"
echo "  • What's the ceiling height in meat prep?"
echo "  • Is there a conflict between trellis and HVAC?"
echo "  • What are the grid dimensions?"
echo "  • Who is the general contractor?"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Keep script running and handle shutdown
trap "echo -e '\n${YELLOW}Shutting down server...${NC}'; kill $SERVER_PID 2>/dev/null; exit 0" INT TERM

# Wait for server process
wait $SERVER_PID