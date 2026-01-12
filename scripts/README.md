# 🚀 Construction Agent Startup Scripts

Automated scripts to set up and run the Construction Agent POC with a single command.

## Quick Start

### macOS/Linux
```bash
cd simple-agent/scripts
./start.sh
```

### Windows/Cross-Platform
```bash
cd simple-agent/scripts
python start.py
```

## What the Scripts Do

Both scripts perform the same steps:

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

## Stopping the Server

Press `Ctrl+C` in the terminal where the script is running.

The script will cleanly shut down the server.