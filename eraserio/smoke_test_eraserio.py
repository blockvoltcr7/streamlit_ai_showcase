import requests
import os
from dotenv import load_dotenv

load_dotenv()


# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")


url = "https://app.eraser.io/api/render/prompt"

text = """
ESG-Focused Wealth Management API Flow:
1. Client requests portfolio analysis
2. System calls Financial Data API
3. Financial Data API returns stock data with ESG scores
4. System extracts ESG scores from response
5. System prompts client for ESG preferences
6. Client selects focus area:
   Environmental: Go to step 7
   Social: Go to step 8
   Governance: Go to step 9
   All factors equally: Go to step 10
7. System calls Custom ESG Calculation API with environmental scores only
   Go to step 11
8. System calls Custom ESG Calculation API with social scores only
   Go to step 11
9. System calls Custom ESG Calculation API with governance scores only
   Go to step 11
10. System calls Custom ESG Calculation API with all ESG scores
11. Custom ESG Calculation API returns tailored portfolio score
12. System generates portfolio report with custom ESG analysis
13. System presents report to client
14. Does client want to make changes based on ESG scores?
    Yes: Go to step 15
    No: Go to step 16
15. System provides recommendations for portfolio adjustments
    Return to step 1
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
    
    # Save the image
    output_path = os.path.join(output_dir, "customer_support_workflow.png")
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Image saved successfully at: {output_path}")

except requests.RequestException as e:
    print(f"Error making request: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")