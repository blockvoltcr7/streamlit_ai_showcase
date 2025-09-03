"""Gradio UI for generating spoken audio with OpenAI Realtime API.

User enters text -> backend opens a short-lived realtime websocket session,
sends a single response.create request, accumulates base64 PCM16 audio deltas,
converts to a normalized float32 numpy array (shape: (n_samples,)), and returns
it to Gradio for playback along with the transcript text.

This avoids local sounddevice playback issues and plays audio in the browser.
"""
from __future__ import annotations

import os
import json
import base64
import asyncio
import time
import io
import wave
import websockets
from websockets.exceptions import InvalidStatus
import numpy as np
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
assert API_KEY, "Set OPENAI_API_KEY in .env"

REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime"
SAMPLE_RATE = 16000
DEFAULT_VOICE = "marin"


client = OpenAI()


async def _fetch_audio(text: str, voice: str) -> tuple[np.ndarray, str]:
    """Connect to realtime endpoint, request audio for text, return PCM as float array and transcript.

    Returns:
        (audio_float32, transcript_text)
    """
    transcript_parts: list[str] = []
    pcm_chunks: list[bytes] = []

    start_connect = time.monotonic()
    # Attempt connection with simple exponential backoff (handles transient 5xx)
    ws = None
    for attempt in range(3):
        try:
            ws = await websockets.connect(
                REALTIME_URL,
                additional_headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "OpenAI-Beta": "realtime=v1",
                },
                max_size=None,
            )
            break
        except InvalidStatus as e:
            code = getattr(getattr(e, "response", None), "status_code", "?")
            print(f"[realtime connect] HTTP {code} on attempt {attempt+1}")
            if code in (500, 502, 503, 504):
                await asyncio.sleep(0.5 * (2 ** attempt))
                continue
            # Non-retryable status
            return await _fallback_tts(text, voice, transcript_parts, reason=f"connect HTTP {code}")
        except Exception as e:
            print(f"[realtime connect] unexpected error {e} (attempt {attempt+1})")
            await asyncio.sleep(0.5 * (2 ** attempt))
    if ws is None:
        return await _fallback_tts(text, voice, transcript_parts, reason="exhausted retries")

    async with ws:
        # --- Session update ---
        # Configure session (ask for pcm16 output)
        await ws.send(
            json.dumps(
                {
                    "type": "session.update",
                    "session": {
                        "voice": voice,
                        "instructions": "You are a concise helpful assistant.",
                        "modalities": ["text", "audio"],  # ensure audio modality enabled at session scope
                        "output_audio_format": "pcm16",
                    },
                }
            )
        )
        # --- Provide user message as conversation item (newer schema) ---
        await ws.send(
            json.dumps(
                {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": text}
                        ],
                    },
                }
            )
        )
        # --- Ask model to respond (audio + text) ---
        await ws.send(
            json.dumps(
                {
                    "type": "response.create",
                    "response": {
                        "modalities": ["audio", "text"],
                        # Keep only supported output_audio_format (no output_audio)
                        "output_audio_format": "pcm16",
                    },
                }
            )
        )

        last_event_time = time.monotonic()
        TIMEOUT = 25  # seconds without any event -> break
        DEBUG_LIMIT = 10  # first N events printed to server log
        event_count = 0
        try:
            async for raw in ws:
                event_count += 1
                msg = json.loads(raw)
                mtype = msg.get("type")
                last_event_time = time.monotonic()
                if event_count <= DEBUG_LIMIT:
                    print(f"[realtime debug] event {event_count}: {mtype}")
                if mtype in ("response.output_text.delta", "response.audio_transcript.delta"):
                    delta = msg.get("delta", "")
                    if delta:
                        transcript_parts.append(delta)
                elif mtype in ("response.audio.delta", "response.output_audio.delta"):
                    # Accept several possible field names for base64 payload
                    b64 = msg.get("delta") or msg.get("audio") or msg.get("chunk")
                    if b64:
                        raw_bytes = base64.b64decode(b64)
                        pcm_chunks.append(raw_bytes)
                        if event_count <= DEBUG_LIMIT:
                            print(
                                f"[realtime debug] received audio bytes: {len(raw_bytes)} (total={sum(len(c) for c in pcm_chunks)})"
                            )
                elif mtype and mtype.startswith("response.completed"):
                    break
                else:
                    # Keep an eye out for new audio event naming; print first few.
                    if event_count <= DEBUG_LIMIT:
                        print(f"[realtime debug] unhandled event body: {msg}")
                # Safety: cap runtime
                if time.monotonic() - last_event_time > TIMEOUT:
                    print("[realtime warning] timeout waiting for events; breaking")
                    break
        except Exception as e:
            print("[realtime error]", e)

    # Combine audio and convert to float32 normalized [-1,1]
    pcm_bytes = b"".join(pcm_chunks)
    if pcm_bytes:
        int16_audio = np.frombuffer(pcm_bytes, dtype=np.int16)
        audio = (int16_audio.astype(np.float32) / 32768.0)
        transcript = "".join(transcript_parts)
        return audio, transcript

    # Fallback: realtime yielded no bytes
    return await _fallback_tts(text, voice, transcript_parts, reason="no realtime audio frames")


async def _fallback_tts(text: str, voice: str, transcript_parts: list[str], reason: str):
    try:
        print(f"[realtime fallback] Using TTS endpoint due to: {reason}")
        tts = client.audio.speech.create(
            model="gpt-4o-mini-tts", voice=voice, input=text, format="wav"
        )
        wav_bytes = tts.read() if hasattr(tts, "read") else tts
        if isinstance(wav_bytes, str):
            wav_bytes = base64.b64decode(wav_bytes)
        with wave.open(io.BytesIO(wav_bytes), "rb") as w:
            sr = w.getframerate()
            frames = w.readframes(w.getnframes())
        int16_audio = np.frombuffer(frames, dtype=np.int16)
        audio = int16_audio.astype(np.float32) / 32768.0
        transcript = "".join(transcript_parts) + f" (fallback TTS: {reason})"
        global SAMPLE_RATE
        SAMPLE_RATE = sr
        return audio, transcript
    except Exception as e:
        print("[fallback error]", e)
        transcript = (
            "".join(transcript_parts)
            + f" (No audio produced; fallback failed: {e})"
        )
        return np.zeros(1, dtype=np.float32), transcript


async def generate_audio(text: str, voice: str) -> tuple[tuple[int, np.ndarray], str]:
    if not text or not text.strip():
        return (SAMPLE_RATE, np.zeros(1, dtype=np.float32)), "(No text provided)"
    audio, transcript = await _fetch_audio(text.strip(), voice)
    return (SAMPLE_RATE, audio), transcript


with gr.Blocks(title="OpenAI Realtime Voice") as demo:
    gr.Markdown("## OpenAI Realtime Voice\nEnter text and get synthesized speech back through the browser.")
    with gr.Row():
        txt = gr.Textbox(label="Prompt", placeholder="Say something motivational…", lines=2)
        voice = gr.Dropdown(
            label="Voice",
            choices=["marin", "cedar"],
            value=DEFAULT_VOICE,
        )
    btn = gr.Button("Speak")
    audio_out = gr.Audio(label="Generated Audio", type="numpy")
    transcript_out = gr.Textbox(label="Transcript", interactive=False)

    btn.click(fn=generate_audio, inputs=[txt, voice], outputs=[audio_out, transcript_out])

if __name__ == "__main__":
    # Launch on localhost
    demo.launch()
