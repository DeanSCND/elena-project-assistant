#!/bin/bash

# Elena Construction Agent - Stop All Services

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Configuration
BACKEND_PORT=8100
FRONTEND_PORT=5174

echo -e "${YELLOW}Stopping Elena Construction Agent...${NC}"

# Kill processes on ports
if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
    echo -e "Stopping backend (port $BACKEND_PORT)..."
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✓ Backend stopped${NC}"
else
    echo "Backend not running"
fi

if lsof -ti:$FRONTEND_PORT > /dev/null 2>&1; then
    echo -e "Stopping frontend (port $FRONTEND_PORT)..."
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✓ Frontend stopped${NC}"
else
    echo "Frontend not running"
fi

# Stop Firestore if running
if docker ps | grep -q firestore; then
    echo -e "\nFirestore emulator is running."
    read -p "Stop Firestore emulator? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down
        echo -e "${GREEN}✓ Firestore stopped${NC}"
    fi
fi

echo -e "\n${GREEN}✓ All services stopped${NC}"
