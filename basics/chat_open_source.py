import streamlit as st
import os
from openai import OpenAI
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Set up the Streamlit application title
st.title("Multi-AI Provider Chat Clone")

model_provider = st.selectbox(
    "Select model provider:",
    ("OpenAI", "Claude AI", "Together AI")
)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')

print(OPENAI_API_KEY)
print(ANTHROPIC_API_KEY)
print(TOGETHER_API_KEY)

# Initialize the appropriate client based on the selected provider
if model_provider == "OpenAI":
    client = OpenAI(api_key=OPENAI_API_KEY)
    model = "gpt-3.5-turbo"
elif model_provider == "Claude AI":
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    model = "claude-2"
elif model_provider == "Together AI":
    client = OpenAI(api_key=TOGETHER_API_KEY, base_url="https://api.together.xyz")
    model = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Set up session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
prompt = st.chat_input("What is up?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        if model_provider in ["OpenAI", "Together AI"]:
            for response in client.chat.completions.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
        elif model_provider == "Claude AI":
            prompt = ""
            for m in st.session_state.messages:
                if m["role"] == "user":
                    prompt += f"{HUMAN_PROMPT} {m['content']}"
                else:
                    prompt += f"{AI_PROMPT} {m['content']}"
            prompt += f"{HUMAN_PROMPT} {st.session_state.messages[-1]['content']}{AI_PROMPT}"
            
            stream = client.completions.create(
                model=model,
                prompt=prompt,
                max_tokens_to_sample=300,
                stream=True,
            )
            for completion in stream:
                full_response += (completion.completion or "")
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    
    # Append assistant's response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})