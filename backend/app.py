#!/usr/bin/env python3
"""
Simple Construction Agent POC
Conversational interface for Aurora construction documents
"""

import os
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Dict, Any, Optional
from datetime import datetime
import uuid
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import tempfile
import base64
import httpx

from openai import AsyncOpenAI

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize FastAPI app
app = FastAPI(title="Construction Agent POC")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global context storage
AURORA_CONTEXT = {}
CONSTRUCTION_EXPERT_PROMPT = """You are an expert construction field assistant with deep knowledge of the Aurora Food Store project in Regina, SK.

You have access to comprehensive documentation including:
- IFC (Issued for Construction) drawings dated March 25, 2025
- Reflected Ceiling Plans (RCP) showing ceiling types and heights
- Shop drawings for trellis systems, equipment, and fixtures
- PCN clarifications and field verification documents
- Detailed AI analysis of all drawings with dimensions, specifications, and potential conflicts

When answering questions:
1. Be specific and cite sources (e.g., "per F4.1 RCP, section 1.1")
2. Use exact dimensions and specifications from the documents
3. Alert users to any potential conflicts or coordination issues
4. Provide practical field guidance
5. If information is unclear or missing, say so

Key project facts:
- Location: 2000 Anaquod Road, Regina, SK
- Owner: Sobeys Inc.
- General Contractor: Quorex Construction Services Ltd.
- Building area: ~55,800 SF
- Grid system: A-J (horizontal) x 1-13 (vertical)
"""

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class VoiceConfig(BaseModel):
    enabled: bool = False
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice

# Load documents at startup
def load_aurora_documents() -> Dict[str, str]:
    """Load all Aurora project documents into memory"""
    context = {}

    # Try both potential paths
    possible_paths = [
        Path("../Aurora (Safeway) Regina, SK"),
        Path(__file__).parent.parent.parent / "Aurora (Safeway) Regina, SK"
    ]

    aurora_path = None
    for path in possible_paths:
        if path.exists():
            aurora_path = path
            break

    if not aurora_path:
        print(f"Warning: Aurora path not found. Tried:")
        for path in possible_paths:
            print(f"  - {path.absolute()}")
        return context

    print(f"Loading Aurora project documents from: {aurora_path.absolute()}")

    # Load all .AI.md files (comprehensive analysis)
    ai_files = list(aurora_path.glob("**/*.AI.md"))
    for ai_file in ai_files:
        try:
            with open(ai_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                context[ai_file.name] = content
                print(f"  ✓ Loaded {ai_file.name} ({len(content):,} chars)")
        except Exception as e:
            print(f"  ✗ Error loading {ai_file.name}: {e}")

    # Load key markdown extractions
    key_files = [
        "Aurora Food Store IFC Drawings (March 25, 2025).md",
        "FIELD_VERIFICATION_HVAC_TRELLIS_CLEARANCE.md",
        "QUICK_FIELD_CHECK_HVAC_TRELLIS.md",
        "QUOREX_SITE_INSTRUCTION_HVAC_TRELLIS.md"
    ]

    for filename in key_files:
        file_path = aurora_path / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Limit main extraction to first 50K chars for POC
                    if filename == "Aurora Food Store IFC Drawings (March 25, 2025).md":
                        content = content[:50000]
                    context[filename] = content
                    print(f"  ✓ Loaded {filename} ({len(content):,} chars)")
            except Exception as e:
                print(f"  ✗ Error loading {filename}: {e}")

    total_chars = sum(len(v) for v in context.values())
    print(f"\nTotal context loaded: {total_chars:,} characters (~{total_chars//4:,} tokens)")
    print(f"Documents loaded: {len(context)}")

    return context

def format_context_for_llm(context: Dict[str, str]) -> str:
    """Format document context for LLM consumption"""
    formatted = "# PROJECT DOCUMENTATION\n\n"

    for filename, content in context.items():
        formatted += f"## Document: {filename}\n\n"
        formatted += content[:20000] if len(content) > 20000 else content  # Limit each doc
        formatted += "\n\n---\n\n"

    return formatted

# AG-UI Event formatting functions
def format_sse_event(event_type: str, data: Any) -> str:
    """Format event as Server-Sent Event"""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    return f"data: {json.dumps(event)}\n\n"

async def stream_llm_response(query: str, context: str, model: str = "gpt-4o") -> AsyncGenerator[str, None]:
    """Stream LLM response with AG-UI events"""

    # Send RUN_STARTED event
    yield format_sse_event("RUN_STARTED", {
        "run_id": str(uuid.uuid4()),
        "query": query
    })

    # Send TEXT_MESSAGE_START event
    yield format_sse_event("TEXT_MESSAGE_START", {
        "role": "assistant"
    })

    try:
        # Check if client is properly initialized
        if not openai_client:
            raise ValueError("OpenAI client not initialized. Check your API key.")

        # Limit context size to avoid token limits
        max_context_chars = 50000  # Roughly 12.5k tokens
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n\n[Context truncated for length...]"

        # Combine system prompt with context
        system_message = CONSTRUCTION_EXPERT_PROMPT + "\n\n" + context

        print(f"Sending query to OpenAI: {query[:100]}...")
        print(f"Context size: {len(context)} chars")

        # OpenAI streaming
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            stream=True,
            temperature=0.3,
            max_tokens=2000
        )

        full_response = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                text_chunk = chunk.choices[0].delta.content
                full_response += text_chunk
                # Send TEXT_MESSAGE_CHUNK event
                yield format_sse_event("TEXT_MESSAGE_CHUNK", {
                    "content": text_chunk
                })

        print(f"Response complete: {len(full_response)} chars")

    except Exception as e:
        print(f"Error in stream_llm_response: {e}")
        import traceback
        traceback.print_exc()

        yield format_sse_event("RUN_ERROR", {
            "error": str(e)
        })
        return

    # Send TEXT_MESSAGE_END event
    yield format_sse_event("TEXT_MESSAGE_END", {
        "full_text": full_response
    })

    # Send RUN_FINISHED event
    yield format_sse_event("RUN_FINISHED", {
        "status": "success"
    })

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Load documents when server starts"""
    global AURORA_CONTEXT
    AURORA_CONTEXT = load_aurora_documents()
    if not AURORA_CONTEXT:
        print("\n⚠️  Warning: No documents loaded. Check Aurora folder path.")

@app.get("/")
async def root():
    """Serve the frontend"""
    return HTMLResponse("""
    <html>
        <head>
            <title>Construction Agent POC</title>
        </head>
        <body>
            <h1>Construction Agent POC</h1>
            <p>API is running. Open <a href="/chat">frontend/index.html</a> for the chat interface.</p>
            <p>Documents loaded: """ + str(len(AURORA_CONTEXT)) + """</p>
        </body>
    </html>
    """)

@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """Handle chat messages with SSE streaming"""
    try:
        if not AURORA_CONTEXT:
            raise HTTPException(status_code=500, detail="No documents loaded")

        # Check if OpenAI client is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Format context for this query
        context = format_context_for_llm(AURORA_CONTEXT)

        # Use OpenAI GPT-4
        model = "gpt-4o"

        # Return streaming response
        return StreamingResponse(
            stream_llm_response(message.message, context, model),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable proxy buffering
            }
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for bidirectional communication"""
    await websocket.accept()

    if not AURORA_CONTEXT:
        await websocket.send_json({
            "type": "error",
            "message": "No documents loaded"
        })
        await websocket.close()
        return

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            if data.get("type") == "chat":
                # Format context
                context = format_context_for_llm(AURORA_CONTEXT)

                # Stream response back via WebSocket
                await websocket.send_json({
                    "type": "RUN_STARTED",
                    "data": {"query": data.get("message")}
                })

                # Process with OpenAI
                model = "gpt-4o"

                async for event in stream_llm_response(data.get("message"), context, model):
                    # Parse SSE format and send as JSON
                    if event.startswith("data: "):
                        event_data = json.loads(event[6:].strip())
                        await websocket.send_json(event_data)

            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key = os.getenv("OPENAI_API_KEY")
    return {
        "status": "healthy",
        "documents_loaded": len(AURORA_CONTEXT),
        "total_context_size": sum(len(v) for v in AURORA_CONTEXT.values()),
        "openai_configured": bool(api_key),
        "api_key_preview": f"{api_key[:7]}..." if api_key else None,
        "documents": list(AURORA_CONTEXT.keys())[:5] if AURORA_CONTEXT else []
    }

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio using OpenAI Whisper"""
    try:
        # Check if OpenAI client is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Transcribe with Whisper
            with open(tmp_path, "rb") as audio_file:
                transcript = await openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language="en"
                )

            return {"text": transcript}

        finally:
            # Clean up temp file
            os.unlink(tmp_path)

    except Exception as e:
        print(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech")
async def text_to_speech(request: dict):
    """Convert text to speech using OpenAI TTS or ElevenLabs"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")

        # Check for ElevenLabs API key first
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

        if elevenlabs_key:
            # Use ElevenLabs for better quality
            voice_id = request.get("voice_id", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": elevenlabs_key
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "style": 0.0,
                            "use_speaker_boost": True
                        }
                    }
                )

                if response.status_code == 200:
                    audio_content = response.content
                    return Response(
                        content=audio_content,
                        media_type="audio/mpeg",
                        headers={"Content-Disposition": "inline; filename=speech.mp3"}
                    )
                else:
                    print(f"ElevenLabs error: {response.text}")
                    # Fall back to OpenAI TTS

        # Use OpenAI TTS as fallback
        response = await openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",  # or "alloy", "echo", "fable", "onyx", "shimmer"
            input=text,
            response_format="mp3"
        )

        audio_content = response.content
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )

    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-chat")
async def test_chat():
    """Test endpoint for debugging"""
    test_query = "What's the ceiling height in meat prep?"

    try:
        if not AURORA_CONTEXT:
            return {"error": "No documents loaded", "context": AURORA_CONTEXT}

        if not os.getenv("OPENAI_API_KEY"):
            return {"error": "No OpenAI API key", "env_vars": list(os.environ.keys())}

        # Try a simple non-streaming test
        context = format_context_for_llm(AURORA_CONTEXT)[:10000]  # Small test

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a construction assistant. Answer briefly."},
                {"role": "user", "content": test_query}
            ],
            max_tokens=100
        )

        return {
            "success": True,
            "query": test_query,
            "response": response.choices[0].message.content,
            "context_size": len(context),
            "documents_loaded": len(AURORA_CONTEXT)
        }

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "documents_loaded": len(AURORA_CONTEXT),
            "api_key_set": bool(os.getenv("OPENAI_API_KEY"))
        }

if __name__ == "__main__":
    print("\n🚀 Starting Construction Agent POC Server")
    print("=" * 50)

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not found!")
        print("Set OPENAI_API_KEY in .env file")

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)