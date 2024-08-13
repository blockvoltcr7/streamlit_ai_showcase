import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Specify the path to your .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"Looking for .env file at: {dotenv_path}")
print(f".env file exists: {os.path.exists(dotenv_path)}")

load_dotenv(dotenv_path)

# Ensure environment variables are loaded correctly
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2023-05-15"  # Update this to the latest stable version
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

print(f"API Key: {'*' * len(api_key) if api_key else 'Not found'}")
print(f"Azure Endpoint: {azure_endpoint or 'Not found'}")
print(f"Deployment Name: {deployment_name or 'Not found'}")

if not api_key or not azure_endpoint or not deployment_name:
    raise ValueError("Missing API key, endpoint, or deployment name in environment variables.")

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

# Function to send a query and get a response
def query_azure_openai(prompt):
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Test query
test_prompt = "What is the capital of France?"
print("\nSending test query:", test_prompt)

response = query_azure_openai(test_prompt)
print("\nResponse from Azure OpenAI:")
print(response)