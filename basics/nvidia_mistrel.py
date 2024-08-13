import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Get the API key from the environment variable
ngc_api_key = os.getenv('NGC_API_KEY')

if ngc_api_key is None:
    raise ValueError("API key not found. Please set the NGC_API_KEY environment variable.")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=ngc_api_key
)

st.title("Mistral AI Chat Interface")

user_prompt = st.text_area("Enter your prompt:", "Write me a poem about...")

if st.button("Generate Response"):
    if user_prompt:
        with st.spinner("Generating response..."):
            completion = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct-v0.2",
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.5,
                top_p=1,
                max_tokens=1024,
                stream=True
            )

            response = ""
            response_container = st.empty()
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
                    response_container.markdown(response)
    else:
        st.warning("Please enter a prompt before generating a response.")