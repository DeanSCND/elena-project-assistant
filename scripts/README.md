# 🚀 Elena Construction Agent - Startup Scripts

Automated scripts to manage all Elena services with a single command.

## Quick Start (Recommended)

### Start All Services
```bash
cd simple-agent
./scripts/start-all.sh
```

This comprehensive script:
- ✅ Checks and validates environment (.env file, API keys)
- ✅ Cleans up any existing processes on required ports
- ✅ Installs all dependencies (backend & frontend)
- ✅ Optionally starts Firestore emulator for conversation persistence
- ✅ Starts backend API (port 8100)
- ✅ Starts frontend UI (port 5174)
- ✅ Shows all URLs and process information
- ✅ Manages graceful shutdown on Ctrl+C

### Stop All Services
```bash
./scripts/stop-all.sh
```

## Alternative Startup Methods

### V2 Script (Frontend + Backend)
```bash
./scripts/start-v2.sh
```

### Legacy Scripts
```bash
# macOS/Linux
./scripts/start.sh

# Windows/Cross-Platform
python scripts/start.py
```

## Service Components

Elena consists of multiple components:

1. **Backend API** (Port 8100)
   - FastAPI server
   - AI/LLM integration (OpenAI)
   - Vector search (Pinecone)
   - Document analysis and citations
   - PDF serving

2. **Frontend UI** (Port 5174)
   - Vite dev server
   - HTML/CSS/JavaScript interface
   - PDF viewer with citation support
   - Dark mode support
   - Conversation history

3. **Firestore Emulator** (Port 8080) - Optional
   - Local conversation persistence
   - Docker-based emulator
   - Enable with docker-compose

## Script Details

### `start-all.sh` - Comprehensive Startup (Recommended)

**What it does:**
1. Validates environment (.env, API keys)
2. Kills any existing processes on required ports
3. Installs backend dependencies (Poetry)
4. Installs frontend dependencies (npm/yarn)
5. Creates necessary config files (vite.config.js, etc.)
6. Optionally starts Firestore emulator
7. Starts backend with health check
8. Starts frontend
9. Displays all access URLs and process info
10. Manages graceful cleanup on exit

**Features:**
- ✅ Automatic port conflict resolution
- ✅ Dependency installation
- ✅ Service health checks
- ✅ Log file creation (logs/backend.log, logs/frontend.log)
- ✅ Process tracking
- ✅ Clean shutdown handling

### `stop-all.sh` - Stop All Services

Cleanly stops all running Elena services:
- Kills backend process (port 8100)
- Kills frontend process (port 5174)
- Optionally stops Firestore emulator

### Legacy Scripts

#### `start-v2.sh`
Original V2 startup script. Similar to `start-all.sh` but:
- Uses Qdrant instead of Pinecone
- Less comprehensive error handling
- Different port configurations

#### `start.sh` / `start.py`
Legacy POC scripts. Both perform these steps:

1. **Check Python** - Verifies Python 3.11+ is installed
2. **Install Poetry** - Installs if not present
3. **Configure Environment** - Creates .env and prompts for OpenAI key
4. **Verify Documents** - Checks Aurora project files exist
5. **Install Dependencies** - Runs `poetry install`
6. **Check Port** - Ensures port 8000 is available (or prompts for alternative)
7. **Start Backend** - Launches FastAPI server with Poetry
8. **Open Browser** - Automatically opens the chat interface

## Features

✅ **Complete Setup** - Everything from dependencies to launch
✅ **Interactive** - Prompts for API key if missing
✅ **Port Management** - Handles port conflicts gracefully
✅ **Cross-Platform** - Python script works on all OS
✅ **Error Handling** - Clear messages when something goes wrong
✅ **Colored Output** - Visual feedback during setup

## Script Comparison

| Feature | `start.sh` | `start.py` |
|---------|------------|------------|
| Platform | macOS/Linux | All platforms |
| Requirements | Bash shell | Python only |
| Colors | ✅ Full support | ✅ Auto-detects terminal |
| Speed | Faster | Slightly slower |
| Port kill | lsof/kill | Cross-platform |

## Troubleshooting

### Permission Denied
```bash
# Make scripts executable
chmod +x start.sh start.py
```

### Poetry Not Found
The scripts will auto-install Poetry, but if it fails:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Port Already in Use
The scripts will prompt you to:
1. Kill the existing process
2. Choose a different port
3. Cancel and handle manually

### API Key Issues
- Script prompts for key if missing
- You can manually edit `.env` file
- Key format: `OPENAI_API_KEY=sk-...`

## Manual Commands

If you prefer to run manually:

```bash
# Install dependencies
cd ../backend
poetry install

# Set up environment
cp ../.env.example ../.env
# Edit .env and add OPENAI_API_KEY

# Start server
poetry run python app.py

# Open browser to frontend/index.html
```

## Quick Reference

### View Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Both logs simultaneously
tail -f logs/*.log
```

### Check Service Status
```bash
# Check if ports are in use
lsof -i:8100  # Backend
lsof -i:5174  # Frontend
lsof -i:8080  # Firestore emulator

# Check if services respond
curl http://localhost:8100/health
curl http://localhost:5174
```

### Firestore Emulator
```bash
# Start emulator
docker-compose up -d

# Stop emulator
docker-compose down

# View logs
docker-compose logs -f
```

### Troubleshooting

**Port already in use?**
```bash
# Use stop script
./scripts/stop-all.sh

# Or manually kill processes
lsof -ti:8100 | xargs kill -9
lsof -ti:5174 | xargs kill -9
```

**Dependencies out of sync?**
```bash
# Backend
cd backend && poetry install

# Frontend
cd frontend && npm install
```

**Clear all and restart?**
```bash
./scripts/stop-all.sh
rm -rf logs/*
./scripts/start-all.sh
```

## Stopping Services

**Recommended:**
```bash
./scripts/stop-all.sh
```

**Alternative:**
Press `Ctrl+C` in the terminal where start-all.sh is running.

The script will cleanly shut down all services.