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

# System Prompt for Eraser.io RAG System Diagram Create a detailed diagram in Eraser.io illustrating a Retrieval-Augmented Generation (RAG) system using Microsoft Azure services and Streamlit. The diagram should include the following components and flows:  1. User Interface:     - Represent a Streamlit app interface     - Show options for document upload and user query input 2. Storage:     - Include Azure Blob Storage for document storage 3. Document Processing:     - Represent Microsoft Document Intelligence     - Show the process of text extraction and understanding 4. Embedding Generation:     - Include a component for generating text embeddings     - You can represent this as part of Azure OpenAI Service 5. Vector Database:     - Represent Azure Cognitive Search with vector capabilities     - Show connections for storing and retrieving embeddings 6. RAG Query Processing:     - Illustrate the flow of a user query through the system     - Show how relevant documents are retrieved from the vector database 7. Language Model:     - Represent Azure OpenAI Service (or a similar LLM)     - Show how it generates responses based on the query and retrieved documents 8. Response Delivery:     - Show the path of the generated response back to the user interface Additional Guidelines:  - Use directional arrows to show the flow of data and processes - Include brief labels or descriptions for each component - Use color coding to differentiate between user interactions, data storage, and processing components - Add a legend to explain any symbols or color coding used Remember to make the diagram clear and easy to understand, focusing on the key components and their interactions in the RAG system.    # Recommended Diagram Formats for RAG System Architecture 1. **Flowchart**     - **Description**: A traditional flowchart using standard symbols (rectangles for processes, diamonds for decisions, etc.)     - **Pros**:          - Familiar to most audiences         - Clear representation of sequence and logic     - **Cons**:          - Can become complex for systems with many parallel processes 2. **Data Flow Diagram (DFD)**     - **Description**: Focuses on the flow of data between different processes and data stores     - **Pros**:          - Emphasizes data movement, which is crucial in a RAG system         - Can show multiple processes happening simultaneously     - **Cons**:          - May not capture all logical decisions in the system 3. **Systems Architecture Diagram**     - **Description**: A high-level view showing major components and their interactions     - **Pros**:          - Provides a clear overview of the entire system         - Good for stakeholder communication     - **Cons**:          - May lack detail on internal processes 4. **Swimlane Diagram**     - **Description**: Divides processes into lanes, often representing different components or services     - **Pros**:          - Clearly shows which component is responsible for each process         - Good for systems with distinct services (e.g., Document Intelligence, Vector Database)     - **Cons**:          - Can become cluttered if there are many interactions between lanes 5. **UML Sequence Diagram**     - **Description**: Shows the sequence of interactions between components over time     - **Pros**:          - Excellent for showing the order of operations         - Clear representation of how components communicate     - **Cons**:          - Can be complex for non-technical audiences         - May not capture the overall system structure as clearly Recommendation: For the RAG system we discussed, I would suggest using a combination of a **Systems Architecture Diagram** for the overall view, with embedded **Data Flow Diagram** elements to show the movement of data through the system.  This hybrid approach allows you to:  1. Clearly show the major components (Streamlit app, Azure Blob Storage, Document Intelligence, Vector Database, etc.) 2. Illustrate the flow of data from document upload through processing to query response 3. Highlight the key processes within each component When creating this in Eraser.io, you can use different shapes and colors to distinguish between components, data stores, and processes. Use arrows to show the flow of data and include brief labels to explain each step.
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