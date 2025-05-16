from openai import OpenAI
import base64
import os

client = OpenAI()

result = client.images.generate(
    model="gpt-image-1",
    prompt="a pixel art style of a miyamoto musashi in different fight poses",
    size="1024x1024",
    background="transparent",
    quality="high",
)

# Access the image data directly using the correct attribute path
image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
os.makedirs("output", exist_ok=True)
with open("output/miyamoto_musashi.png", "wb") as f:
    f.write(image_bytes)