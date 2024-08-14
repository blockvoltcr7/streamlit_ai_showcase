import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")



url = "https://app.eraser.io/api/render/prompt"



text_body = """
create a cloud architecture diagram for a google cloud login system with a user, a login, and a session to read from a vector database to execute quereis using llama index to query documents
"""

payload = {
    "text": text_body,
    "diagramType": "cloud-architecture-diagram",
    "background": True,
    "theme": "dark",
    "scale": "3",
    "returnFile": True
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes

    #print status code
    print(f"Status code: {response.status_code}")

    # Print the response text
    print("Response:")
    print(response.content)
    
    # Print response headers
    print("Response Headers:")
    print(response.headers)

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("output", "cloud-architecture-diagram")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Generate a random file name
    random_file_name = f"cloud_arch_diagram_{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, random_file_name)
    
    # Save the image
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Image saved successfully at: {output_path}")
except requests.RequestException as e:
    print(f"Error making request: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")