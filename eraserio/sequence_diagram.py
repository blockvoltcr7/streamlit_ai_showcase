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

User > Frontend: Open application
Frontend > User: Display login form

User > Frontend: Enter credentials
Frontend > Backend: Send login request

Backend > Database: Verify credentials
Database > Backend: Return user data

alt [label: If credentials valid] {
  Backend > Frontend: Send success response
  Frontend > User: Display dashboard
}
else [label: If credentials invalid] {
  Backend > Frontend: Send error response
  Frontend > User: Display error message
  Frontend > User: Prompt to try again
}

User > Frontend: Request to create AI image
Frontend > Backend: Send image creation request

Backend > AI Service: Request image generation
activate AI Service
AI Service > AI Service: Generate image
AI Service > Backend: Return generated image
deactivate AI Service

Backend > Frontend: Send generated image
Frontend > User: Display generated image

User > Frontend: Save or share image
Frontend > Backend: Send save/share request
Backend > Database: Store image metadata
Backend > Frontend: Confirm save/share
Frontend > User: Display confirmation
"""

payload = {
    "text": text_body,
    "diagramType": "sequence-diagram",
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
    output_dir = os.path.join("output", "sequence-diagram")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a random file name
    random_file_name = f"sequence_{uuid.uuid4().hex}.png"
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