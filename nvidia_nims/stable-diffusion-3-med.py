from PIL import Image
import io
import requests, base64
from dotenv import load_dotenv
import os
import json
import random

load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("NGC_API_KEY")
if api_key is None:
    raise ValueError("NGC_API_KEY environment variable is not set")

invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"

headers = {
  "Authorization": f"Bearer {api_key}",
    "Accept": "application/json",
}

payload = {
    "prompt": "Illustration of an angelic heavenly warrior with a golden helmet, a faceless face of bright white light, and flaming blue eyes. The warrior has angel wings and holds a golden spear and shield. The background is filled with celestial light in indigo, violet, and blue",
    "cfg_scale": 5,
    "aspect_ratio": "16:9",
    "seed": 0,
    "steps": 50,
    "negative_prompt": ""
}

response = requests.post(invoke_url, headers=headers, json=payload)

response.raise_for_status()
response_body = response.json()
#response get image from the response get attribute from json object named "image"
image_url = response_body["image"]
# Decode the base64 string
image_data = base64.b64decode(image_url.strip())
# Convert to an image object
image = Image.open(io.BytesIO(image_data))

# Generate a random number
random_number = random.randint(1000, 9999)

# Construct the directory path
directory_path = "..\\images"

# Ensure the directory exists
if not os.path.exists(directory_path):
    os.makedirs(directory_path)

# Construct the filename with the random number
filename = f"{directory_path}\\decoded_image_{random_number}.png"

# Save the image with the new filename
image.save(filename)