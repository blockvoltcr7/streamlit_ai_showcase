import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")


url = "https://app.eraser.io/api/render/prompt"

payload = {
    "text": """title ESG-Focused Wealth Management Process

actor Client
participant "Wealth Management System" as WMS
participant "Financial Data API" as FDA
participant "Custom ESG Calculation API" as CECA

Client->WMS: Request portfolio analysis
WMS->FDA: Request stock data with ESG scores
FDA-->WMS: Return stock data with ESG scores
WMS->Client: Prompt for ESG preferences
Client-->WMS: Select focus area (Environmental/Social/Governance/All)
WMS->CECA: Send selected ESG scores based on focus
CECA-->WMS: Return tailored portfolio score
WMS->WMS: Generate portfolio report
WMS->Client: Present portfolio report
Client->WMS: Decision on portfolio changes
alt Client wants changes
    WMS->WMS: Generate recommendations
    WMS->Client: Present recommendations
    Client->WMS: Approve changes
    WMS->WMS: Implement portfolio adjustments
else Client doesn't want changes
    WMS->WMS: Finalize report
end
WMS->Client: Confirm process completion""",
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

    # Print response headers
    print("Response Headers:")
    print(response.headers)

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("output", "sequence-diagram")
    os.makedirs(output_dir, exist_ok=True)
    

    # Save the image
    output_path = os.path.join(output_dir, "sequence_diagram-1.png")
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Image saved successfully at: {output_path}")

except requests.RequestException as e:
    print(f"Error making request: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")