import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")

print(f"API key: {api_key}")
# Set the API key in the header


url = "https://app.eraser.io/api/render/prompt"



text_body = """
Our Azure architecture for the Streamlit app prioritizes high availability and scalability. We'll deploy the app as a Docker container within Azure Container Instances (ACI) for rapid provisioning and elastic scaling. To ensure resilience, we'll configure multiple ACI instances across different availability zones. Load Balancing will distribute traffic evenly, and Application Insights will monitor performance metrics. For data storage, we'll use Azure Blob Storage for static assets and Azure Cosmos DB for rapid, low-latency data access. To prevent crashes, robust error handling and logging are essential. We'll implement automatic scaling based on CPU utilization and response time, allowing the app to gracefully handle increased load.
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

    # Print response headers
    print("Response Headers:")
    print(response.headers)

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("output", "cloud-architecture-diagram")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a random file name
    random_file_name = f"cloud_arch_{uuid.uuid4().hex}.png"
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