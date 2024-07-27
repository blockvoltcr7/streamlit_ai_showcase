from PIL import Image
import io
import requests, base64
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("NGC_API_KEY")
if api_key is None:
    raise ValueError("NGC_API_KEY environment variable is not set")

invoke_url = "https://ai.api.nvidia.com/v1/vlm/adept/fuyu-8b"
stream = True

# Resize the image and convert to JPEG before encoding to base64
with Image.open(r"..\eraserio\output\sequence-diagram\sequence_diagram-1.png") as img:
    # Resize the image, maintaining aspect ratio
    img.thumbnail((1024, 1024))  # Adjust the size as needed
    
    # Convert the image to RGB if it's not already (JPEG doesn't support alpha channel)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Save the resized image to a bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode()

assert len(image_b64) < 180_000, "To upload larger images, use the assets API (see docs)"

headers = {
  "Authorization": f"Bearer {api_key}",
  "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
  "messages": [
    {
      "role": "user",
      "content": f'can you explain the sequence diagram in detail. expain it as if we are in a meeting with stakeholders tryint to help them <img src="data:image/jpeg;base64,{image_b64}" />'
    }
  ],
  "max_tokens": 1024,
  "temperature": 0.20,
  "top_p": 0.70,
  "seed": 0,
  "stream": stream
}

response = requests.post(invoke_url, headers=headers, json=payload)

if stream:
    full_content = ""  # Initialize an empty string for the full content
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            # Check if the line starts with 'data: ' and has content beyond it
            if decoded_line.startswith('data: '):
                json_str = decoded_line[6:]
                try:
                    data = json.loads(json_str)
                    content = data["choices"][0]["delta"]["content"]
                    full_content += content
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {decoded_line}")
    print(full_content)  # Print the concatenated content after the loop
else:
    print(response.json())