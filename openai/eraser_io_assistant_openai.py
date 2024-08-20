import streamlit as st
import os
import requests
import uuid
from openai import OpenAI
import json
from dotenv import load_dotenv

    """
    AI Assistant Diagram Generator

    This Python script is a Streamlit application that allows users to generate diagrams based on text descriptions. 
    It utilizes the OpenAI API for conversational interaction and the Eraser.io API to create diagrams. 
    
    Key features:
    - User inputs a request for a diagram
    - OpenAI API processes the request to generate diagram description
    - Eraser.io API creates the diagram based on the generated description
    - The resulting diagram is displayed in the Streamlit app
    - Includes error handling and user feedback mechanisms
    - Supports various diagram types, with cloud architecture diagrams as default

    The application provides an intuitive interface for users to create complex diagrams using natural language input,
    combining the power of AI-driven text processing with professional diagram generation capabilities.
    """

load_dotenv()

# Set the title of the Streamlit app
st.title("AI Assistant Diagram Generator")

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ERASER_API_KEY = os.getenv("ERASER_IO_API_KEY")

def generate_diagram(text_body, diagram_type="cloud-architecture-diagram"):
    """
    Generate a diagram using the Eraser.io API.

    Args:
        text_body (str): The text description of the diagram to generate.
        diagram_type (str): The type of diagram to generate (default is "cloud-architecture-diagram").

    Returns:
        str: The file path of the generated diagram or an error message.
    """
    url = "https://app.eraser.io/api/render/prompt"
    
    # Prepare the payload for the API request
    payload = {
        "text": text_body,
        "diagramType": diagram_type,
        "background": True,
        "theme": "light",
        "scale": "3",
        "returnFile": True
    }

    # Set the headers for the API request
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {ERASER_API_KEY}"
    }

    try:
        # Make the API request to generate the diagram
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Create output directory if it doesn't exist
        output_dir = os.path.join("output", diagram_type)
        os.makedirs(output_dir, exist_ok=True)

        # Generate a unique file name for the diagram
        random_file_name = f"{diagram_type}_{uuid.uuid4().hex}.png"
        output_path = os.path.join(output_dir, random_file_name)
        
        # Save the diagram to the specified path
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    except Exception as e:
        return f"Error generating diagram: {str(e)}"

# Define the function that can be called by the assistant
functions = [
    {
        "name": "generate_diagram",
        "description": "Generate a diagram using the Eraser.io API",
        "parameters": {
            "type": "object",
            "properties": {
                "text_body": {
                    "type": "string",
                    "description": "The text description of the diagram to generate"
                },
                "diagram_type": {
                    "type": "string",
                    "description": "The type of diagram to generate",
                    "enum": ["cloud-architecture-diagram", "flowchart", "sequence-diagram", "mindmap", "entity-relationship-diagram"]
                }
            },
            "required": ["text_body"]
        }
    }
]

def run_conversation(user_input):
    """
    Run a conversation with the AI assistant to generate a diagram.

    Args:
        user_input (str): The user's request for a diagram.

    Returns:
        tuple: A tuple containing the diagram path (or None) and the assistant's response.
    """
    messages = [
        {"role": "system", "content": "You are an AI assistant that helps create diagrams. When a user requests a diagram, use the generate_diagram function to create it."},
        {"role": "user", "content": user_input}
    ]
    
    # Call the OpenAI API to get a response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    
    response_message = response.choices[0].message

    # Check if the assistant called the generate_diagram function
    if response_message.function_call:
        function_name = response_message.function_call.name
        function_args = json.loads(response_message.function_call.arguments)
        
        if function_name == "generate_diagram":
            # Generate the diagram and return the path
            diagram_path = generate_diagram(
                text_body=function_args.get("text_body"),
                diagram_type=function_args.get("diagram_type", "cloud-architecture-diagram")
            )
            return diagram_path, response_message.content
    
    return None, response_message.content

# Text area for user input
user_input = st.text_area("Enter your diagram request:", height=150)

# Send button to generate the diagram
if st.button("Generate Diagram"):
    if user_input:
        with st.spinner("Generating diagram..."):
            diagram_path, assistant_response = run_conversation(user_input)
            
            st.subheader("Assistant's Response:")
            st.write(assistant_response)

            # Display the generated diagram or an error message
            if diagram_path:
                if diagram_path.startswith("Error"):
                    st.error(diagram_path)
                else:
                    st.success("Diagram generated successfully!")
                    st.image(diagram_path, caption="Generated Diagram", use_column_width=True)
            else:
                st.warning("The assistant did not generate a diagram for this request.")
    else:
        st.warning("Please enter a diagram request.")

# Add a button to clear the input and result
if st.button("Clear"):
    st.experimental_rerun()