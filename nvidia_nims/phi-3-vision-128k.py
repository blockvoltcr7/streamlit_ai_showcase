
import requests, base64
from dotenv import load_dotenv
import os
from PIL import Image
import io
import json
import re



load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("NGC_API_KEY")
if api_key is None:
    raise ValueError("NGC_API_KEY environment variable is not set")


invoke_url = "https://ai.api.nvidia.com/v1/vlm/microsoft/phi-3-vision-128k-instruct"
stream = True

# Open the image angelic warriror
# with Image.open(r"..\nvidia_nims\images\angelic_warrior.png") as img:
#     # Resize the image, maintaining aspect ratio
#     img.thumbnail((1024, 1024))  # Example size, adjust as needed
    
#     # Save the resized image to a bytes buffer in a more compressed format (e.g., JPEG)
#     buf = io.BytesIO()
#     img.save(buf, format='JPEG', quality=85)  # Adjust quality as needed
#     image_bytes = buf.getvalue()

# Open the image sequence diagream
with Image.open(r"..\eraserio\output\sequence-diagram\sequence_diagram-1.png") as img:
    # Resize the image, maintaining aspect ratio
    img.thumbnail((1024, 1024))  # Example size, adjust as needed
    
    # Convert the image to RGB if it's RGBA (has an alpha channel)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Save the resized image to a bytes buffer in a more compressed format (e.g., JPEG)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)  # Adjust quality as needed
    image_bytes = buf.getvalue()

# Encode the image bytes to base64
image_b64 = base64.b64encode(image_bytes).decode()

headers = {
  "Authorization": f"Bearer {api_key}",
  "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
  "messages": [
    {
      "role": "user",
      "content": f'describe this diagram as if you are explaining it in a meeting with tech leads. <img src="data:image/png;base64,{image_b64}" />'
    }
  ],
  "max_tokens": 512,
  "temperature": 1.00,
  "top_p": 0.70,
  "stream": stream
}

content_accumulator = ""  # Step 1: Initialize an accumulator for content

try:
    response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            # Remove the 'data: ' prefix before parsing
            if decoded_line.startswith('data: '):
                decoded_line = decoded_line[6:]
            try:
                json_data = json.loads(decoded_line)
                content_piece = json_data["choices"][0]["delta"]["content"]
                content_accumulator += content_piece + " "  # Step 2: Append content to the accumulator
            except json.JSONDecodeError as e:
                print("JSON decoding failed:", e)
                # Handle the error (e.g., by continuing to the next line or logging the error)
except requests.RequestException as e:
    print("Request failed:", e)
    # Handle request errors

# Step 3: After the loop, print or use the accumulated content
print(content_accumulator.strip())  # Print the organized paragraph, stripping any leading/trailing whitespace
