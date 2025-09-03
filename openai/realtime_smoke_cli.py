import os, asyncio, json, base64, numpy as np, sounddevice as sd, websockets
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")
assert API_KEY, "Set OPENAI_API_KEY in .env"

# --- Audio config (16kHz mono PCM16 works well for Realtime voice) ---
SAMPLE_RATE = 16000
CHANNELS = 1
VOICE = "marin"   # or "cedar" (any supported voice)

REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime"

# --- Simple PCM16 player that accepts raw bytes (little-endian int16) ---
class AudioPlayer:
    def __init__(self, samplerate=SAMPLE_RATE):
        self.stream = sd.OutputStream(
            samplerate=samplerate,
            channels=1,
            dtype="int16",
            blocksize=0
        )
        self.stream.start()

    def play_pcm16(self, pcm_bytes: bytes):
        if not pcm_bytes:
            return
        # Convert raw little-endian int16 to numpy array
        audio = np.frombuffer(pcm_bytes, dtype=np.int16)
        if audio.size == 0:
            return
        self.stream.write(audio)

async def main():
    print("Connecting to OpenAI Realtime…")
    # websockets 15.x renamed "extra_headers" -> "additional_headers".
    async with websockets.connect(
        REALTIME_URL,
        additional_headers={
            "Authorization": f"Bearer {API_KEY}",
            "OpenAI-Beta": "realtime=v1",
        },
        max_size=None,
    ) as ws:
        player = AudioPlayer()

        # 1) Configure session: ask for audio out; (you can also set input_audio_format for mic later)
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "voice": VOICE,
                "instructions": "You are a concise voice assistant.",
                "output_audio_format": "pcm16",   # we will receive raw PCM16 chunks
            }
        }))

        # 2) Create a response that the model will speak out. You can change the text here.
        text = input("Type something for the model to speak (e.g., 'Give me a 1-line pep talk'): ")
        await ws.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["audio","text"],
                "instructions": text
            }
        }))

        # 3) Read events; stream audio deltas to speakers
        print("\nStreaming response (you should hear audio)…\n")
        async for raw in ws:
            msg = json.loads(raw)

            # text stream (nice to see alongside audio)
            if msg.get("type") == "response.output_text.delta":
                print(msg.get("delta",""), end="", flush=True)

            # audio stream (base64-encoded PCM16)
            if msg.get("type") == "response.output_audio.delta":
                b64 = msg.get("delta")
                if b64:
                    pcm = base64.b64decode(b64)
                    player.play_pcm16(pcm)

            if msg.get("type") == "response.completed":
                print("\n\n✅ Done.")
                break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")