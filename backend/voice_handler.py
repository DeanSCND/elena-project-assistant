#!/usr/bin/env python3
"""
ElevenLabs Voice Integration for Construction Agent
Handles text-to-speech and speech-to-text
"""

import os
import asyncio
import json
import base64
from typing import Optional, AsyncGenerator
import websockets
from openai import AsyncOpenAI

class VoiceHandler:
    """Handle voice synthesis and recognition"""

    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.elevenlabs_ws = None
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (default)

    async def connect_elevenlabs(self):
        """Establish WebSocket connection to ElevenLabs"""
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment")

        uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input?model_id=eleven_flash_v2_5"

        headers = {
            "xi-api-key": self.elevenlabs_api_key,
        }

        try:
            self.elevenlabs_ws = await websockets.connect(uri, extra_headers=headers)

            # Send initial configuration
            await self.elevenlabs_ws.send(json.dumps({
                "text": " ",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                },
                "generation_config": {
                    "chunk_length_schedule": [120, 160, 250, 290]
                }
            }))

            print("✅ Connected to ElevenLabs WebSocket")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to ElevenLabs: {e}")
            return False

    async def stream_tts(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Stream text to ElevenLabs and yield audio chunks
        Uses WebSocket for real-time streaming
        """
        if not self.elevenlabs_ws:
            await self.connect_elevenlabs()

        if not self.elevenlabs_ws:
            raise ConnectionError("Could not establish ElevenLabs connection")

        try:
            # Split text into chunks for streaming
            chunks = self._split_text_for_streaming(text)

            for i, chunk in enumerate(chunks):
                # Send text chunk
                await self.elevenlabs_ws.send(json.dumps({
                    "text": chunk,
                    "flush": i == len(chunks) - 1  # Flush on last chunk
                }))

                # Receive audio chunks
                while True:
                    try:
                        response = await asyncio.wait_for(
                            self.elevenlabs_ws.recv(),
                            timeout=0.5
                        )

                        data = json.loads(response)

                        if data.get("audio"):
                            # Decode base64 audio
                            audio_bytes = base64.b64decode(data["audio"])
                            yield audio_bytes

                        if data.get("isDone"):
                            break

                    except asyncio.TimeoutError:
                        break

        except Exception as e:
            print(f"Error in TTS streaming: {e}")
            raise

    async def transcribe_audio(self, audio_data: bytes, format: str = "webm") -> str:
        """
        Transcribe audio using OpenAI Whisper API
        """
        try:
            # Save audio to temporary file (Whisper API requires file)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            # Transcribe with Whisper
            with open(temp_path, "rb") as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language="en"
                )

            # Clean up temp file
            os.unlink(temp_path)

            return transcript

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""

    def _split_text_for_streaming(self, text: str, chunk_size: int = 200) -> list:
        """
        Split text into chunks for optimal streaming
        Tries to break at sentence boundaries
        """
        sentences = text.replace("!", ".").replace("?", ".").split(".")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    async def close(self):
        """Close WebSocket connection"""
        if self.elevenlabs_ws:
            await self.elevenlabs_ws.close()
            self.elevenlabs_ws = None


# Example usage for testing
async def test_voice():
    """Test voice functionality"""
    handler = VoiceHandler()

    # Test TTS
    text = "The ceiling height in the meat prep area is 10 feet above finished floor, with ACT2 acoustic tile."

    print("Testing TTS streaming...")
    audio_chunks = []
    async for chunk in handler.stream_tts(text):
        audio_chunks.append(chunk)
        print(f"Received audio chunk: {len(chunk)} bytes")

    print(f"Total audio: {sum(len(c) for c in audio_chunks)} bytes")

    await handler.close()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_voice())