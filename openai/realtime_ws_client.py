"""Minimal OpenAI Realtime WebSocket client using websocket-client (alternative approach).

Features:
 - Connects with websocket-client instead of websockets asyncio library.
 - Sends session.update (enabling audio + chosen voice) then a user message and response.create.
 - Prints every event in pretty JSON.
 - Collects base64 audio frame deltas (several possible event type names) and writes a WAV file when completed.

Usage:
  uv run python realtime_ws_client.py --prompt "Say something inspiring" --voice marin

Notes:
 - If you still get only transcript events (response.audio_transcript.delta) and no audio deltas,
   your account / key may not yet emit synthesized audio for text-only turns.
 - This script purposefully avoids asyncio to mirror the doc example the user provided.
"""
from __future__ import annotations

import os
import json
import argparse
import base64
import wave
import datetime as dt
from pathlib import Path
from typing import List

import websocket  # type: ignore

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY, "Set OPENAI_API_KEY in environment (.env)"

URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime"


def write_wav(pcm16: bytes, samplerate: int, path: Path) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # int16
        w.setframerate(samplerate)
        w.writeframes(pcm16)


def build_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", default="Give me a one line pep talk", help="User text to send")
    ap.add_argument("--voice", default="marin", help="Voice (e.g. marin, cedar, alloy)")
    ap.add_argument("--samplerate", type=int, default=16000, help="Expected PCM16 sample rate")
    ap.add_argument("--out", default="realtime_output.wav", help="Output WAV file if audio frames received")
    ap.add_argument("--direct", action="store_true", help="Skip conversation.item.create; put prompt in response.create.instructions")
    ap.add_argument("--no-audio", action="store_true", help="Do not request audio (debug text only)")
    return ap.parse_args()


def main():
    args = build_args()

    audio_chunks: List[bytes] = []
    transcript_parts: List[str] = []

    headers = [
        "Authorization: Bearer " + OPENAI_API_KEY,
        "OpenAI-Beta: realtime=v1",
    ]

    def log(event: str):
        print(f"[client] {event}")

    def on_open(ws):  # noqa: ANN001
        log("Connected. Sending session + prompts...")
        session = {
            "type": "session.update",
            "session": {
                # no 'type': 'realtime' (causes unknown_parameter)
                "modalities": (["text", "audio"] if not args.no_audio else ["text"]),
                "voice": args.voice,
                **({"output_audio_format": "pcm16"} if not args.no_audio else {}),
                "instructions": "You are a concise helpful assistant.",
            },
        }
        ws.send(json.dumps(session))

        if not args.direct:
            # User message as conversation item
            ws.send(
                json.dumps(
                    {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": args.prompt},
                            ],
                        },
                    }
                )
            )

        # Ask model to respond
        response_payload = {
            "type": "response.create",
            "response": {
                "modalities": (["audio", "text"] if not args.no_audio else ["text"]),
                **({"instructions": args.prompt} if args.direct else {}),
                # Do NOT include invalid output_audio field
                **({"output_audio_format": "pcm16"} if not args.no_audio else {}),
            },
        }
        ws.send(json.dumps(response_payload))

    def on_message(ws, message: str):  # noqa: ANN001
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("[raw]", message)
            return
        etype = data.get("type")
        print("Received:", etype, json.dumps(data, indent=2)[:300])

        # Transcript deltas
        if etype in ("response.output_text.delta", "response.audio_transcript.delta"):
            delta = data.get("delta", "")
            if delta:
                transcript_parts.append(delta)

        # Audio delta frames (several naming variants)
        if etype in ("response.audio.delta", "response.output_audio.delta"):
            b64 = data.get("delta") or data.get("audio") or data.get("chunk")
            if b64:
                audio_chunks.append(base64.b64decode(b64))
                print(f"[audio] total bytes: {sum(len(c) for c in audio_chunks)}")

        if etype and etype.startswith("response.completed"):
            ws.close()

    def on_close(_ws, status_code, msg):  # noqa: ANN001
        log(f"Closed ({status_code}) {msg}")
        if audio_chunks:
            pcm = b"".join(audio_chunks)
            timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%d_%H%M%S")
            out_path = Path(args.out).with_name(f"{Path(args.out).stem}_{timestamp}.wav")
            write_wav(pcm, args.samplerate, out_path)
            print(f"Saved audio -> {out_path}")
        else:
            print("No audio frames captured.")
        if transcript_parts:
            print("Transcript:", "".join(transcript_parts))

    def on_error(_ws, error):  # noqa: ANN001
        print("[error]", error)

    ws = websocket.WebSocketApp(
        URL,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error,
    )

    ws.run_forever()


if __name__ == "__main__":
    main()
