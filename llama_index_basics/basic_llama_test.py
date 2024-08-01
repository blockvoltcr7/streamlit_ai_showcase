import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

"""
This module demonstrates the use of OpenAI's API to generate a Python function.

It loads environment variables, retrieves the OpenAI API key, and generates a function
that calculates the sum of two numbers.
"""

import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

def main() -> None:
    """Main function to execute the OpenAI API call."""
    load_dotenv()
    
    # Ensure the API key is present
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
    
    response = OpenAI(model="gpt-3.5-turbo", api_key=api_key).complete(
        prompt="Create a Python function that calculates the sum of two numbers", 
        max_tokens=100
    )
    
    print(response)

if __name__ == "__main__":
    main()
