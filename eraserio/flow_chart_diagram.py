import requests
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

#flow chart syntax doc https://docs.eraser.io/docs/syntax-3
#flow chart example: https://docs.eraser.io/docs/syntax-3

# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")


url = "https://app.eraser.io/api/render/prompt"

text = """
When a new issue comes in, the first step is to determine if it's a bug or a feature request.
If it's a bug:

Check if it's a duplicate of an existing issue.
If it's not a duplicate, see if there's a way to reproduce the bug.
If there's no reproduction steps, someone needs to ask for them.
Once there's a way to reproduce the bug, it's ready for someone to work on.

If it's a feature request:

First, they check if it could be made into a separate package or module.
If it can be a package, they define it as such.
Then they check if the feature is well-specified (clearly described).
If it's not well-specified, they go back to the packaging question, suggesting some back-and-forth might be needed to clarify the feature.
Once it's well-specified, it's ready for someone to work on.

The main goal for both bugs and features is to get them to a "ready to claim" state, where they're clear and defined enough for development to begin. This process helps organize and prioritize work, ensuring that issues are properly understood and prepared before anyone starts coding.
"""

payload = {
    "text": text, 
    "diagramType": "flowchart-diagram",
    "background": True,
    "theme": "light",
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

    # Print response headers
    print("Response Headers:")
    print(response.headers)

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("output", "flowchart-diagram")
    os.makedirs(output_dir, exist_ok=True)

    # Generate a random file name
    random_file_name = f"flowdiagram-diagram{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, random_file_name)
    
    print(f"Image saved successfully at: {output_path}")

except requests.RequestException as e:
    print(f"Error making request: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")