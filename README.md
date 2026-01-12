# 🏗️ Construction Agent POC

A simple conversational agent for the Aurora Food Store construction project. This POC demonstrates natural language Q&A about construction documents using streaming responses and optional voice interaction.

## Features

- 💬 **Natural language chat** about construction documents
- 🔄 **Real-time streaming responses** using AG-UI protocol events
- 📄 **Full document context** loaded at startup (no vector store needed)
- 🎙️ **Optional voice input** (push-to-talk)
- 🔊 **Voice responses** (browser TTS, with ElevenLabs support)
- 📊 **Source references** from actual project documents

## Quick Start

### 🚀 Automated Setup (Recommended)

Run the all-in-one startup script that handles everything:

```bash
# macOS/Linux
cd simple-agent/scripts
./start.sh

# Windows/Cross-platform
cd simple-agent/scripts
python start.py
```

The script will:
- Check Python and install Poetry if needed
- Prompt for your OpenAI API key
- Install all dependencies
- Start the server
- Open the chat interface in your browser

### Manual Setup

If you prefer to set up manually:

#### 1. Setup Environment with Poetry

```bash
cd simple-agent/backend

# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Copy and configure environment variables
cp ../.env.example ../.env
# Edit .env and add your OpenAI API key
```

#### 2. Add API Keys

Add your OpenAI key to `.env`:

```bash
OPENAI_API_KEY=sk-your-openai-key       # Required for GPT-4

# Optional for voice features:
ELEVENLABS_API_KEY=your-elevenlabs-key  # For high-quality TTS
```

#### 3. Start the Server

```bash
# Using Poetry (recommended)
poetry run python app.py

# Or use the Poetry script
poetry run start
```

You should see:
```
Loading Aurora project documents...
  ✓ Loaded Aurora Food Store IFC Drawings.AI.md (64,507 chars)
  ✓ Loaded F0.1 General Notes.AI.md (62,593 chars)
  ...
Total context loaded: ~500,000 characters (~125,000 tokens)

🚀 Starting Construction Agent POC Server
```

### 4. Open the Chat Interface

Open your browser to: http://localhost:8000

Or open `frontend/index.html` directly in your browser.

## Usage

### Example Queries

Try asking these questions:

- "What's the ceiling height in the meat prep area?"
- "Is there a conflict between the trellis and HVAC?"
- "What are the grid dimensions for the building?"
- "Show me the door specifications"
- "Who is the general contractor?"
- "What's the total building area?"

### Voice Features

1. **Voice Output**: Click "🎙️ Voice Off" to enable voice responses
2. **Voice Input**: Hold the microphone button to speak your question

Note: Voice input requires microphone permissions. The POC uses browser TTS by default.

## Architecture

### Simple POC Design

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (HTML/JS)                 │
│  - Chat interface with streaming support             │
│  - AG-UI event handling                              │
│  - Voice controls (optional)                         │
└─────────────────────────────────────────────────────┘
                           │
                    SSE/WebSocket
                           │
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
│  - Loads all .AI.md files at startup (~500KB)       │
│  - Passes full context with each query              │
│  - Streams responses with AG-UI events              │
│  - Optional ElevenLabs voice integration            │
└─────────────────────────────────────────────────────┘
                           │
                      Direct API
                           │
┌─────────────────────────────────────────────────────┐
│              LLM Provider (OpenAI/Anthropic)        │
│  - GPT-4 or Claude 3.5 Sonnet                       │
│  - ~20K tokens per query (well within limits)       │
└─────────────────────────────────────────────────────┘
```

### AG-UI Events

The system implements AG-UI protocol events for streaming:

- `RUN_STARTED` - Query processing begins
- `TEXT_MESSAGE_START` - Response streaming starts
- `TEXT_MESSAGE_CHUNK` - Each text chunk as it arrives
- `TEXT_MESSAGE_END` - Response complete
- `RUN_FINISHED` - Processing complete
- `RUN_ERROR` - Error handling

### Document Loading

At startup, the system loads:

1. All `.AI.md` files from Aurora project (comprehensive analysis)
2. Key extracted markdown files (limited to 50K chars each)
3. Field verification documents

Total context: ~500K characters (~125K tokens)

This fits easily in modern LLM context windows:
- GPT-4: 128K context
- Claude 3: 200K context

## Customization

### Change the LLM Model

In `backend/app.py`, modify the model selection:

```python
model = "gpt-4o"  # or "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"
```

### Adjust Context Size

To load more/less document context, edit the loading logic in `load_aurora_documents()`.

### Add New Documents

Place additional `.md` or `.AI.md` files in the Aurora folder and restart the server.

## Limitations (POC)

This is a proof-of-concept with intentional simplifications:

- No vector database (loads everything in memory)
- No conversation persistence
- No multi-project support
- Basic error handling
- Browser TTS fallback (ElevenLabs optional)
- No authentication

## Next Steps

To evolve this POC toward the full DESIGN.md vision:

1. **Add vector store** (Pinecone/ChromaDB) for scalability
2. **Implement proper RAG** for selective context retrieval
3. **Add database** for conversation history
4. **Multi-project support** with project selection
5. **Production voice** with ElevenLabs WebSocket
6. **Deploy to cloud** (Railway/AWS Lambda)

## Troubleshooting

### "Backend not connected"
- Ensure the server is running (`python app.py`)
- Check the terminal for error messages
- Verify API keys are set in `.env`

### "No documents loaded"
- Check that the Aurora folder exists at `../Aurora (Safeway) Regina, SK/`
- Verify `.AI.md` files are present in the folder

### Voice not working
- Browser TTS: Check browser compatibility
- ElevenLabs: Verify API key is set
- Microphone: Allow browser permissions

## Cost Estimates

With ~20K tokens per query:

**OpenAI GPT-4o:**
- Input: ~$0.05 per query (20K tokens @ $2.50/1M)
- Output: ~$0.03 per query (1K tokens @ $10/1M)
- Total: ~$0.08 per query

**OpenAI GPT-4:**
- Input: ~$0.60 per query (20K tokens @ $30/1M)
- Output: ~$0.12 per query (1K tokens @ $60/1M)
- Total: ~$0.72 per query

**ElevenLabs:**
- ~$0.18 per 1000 characters
- ~$0.09 per typical response

## Support

This is a POC for testing conversational interfaces with construction documents. For the full system design, see `../DESIGN.md`.