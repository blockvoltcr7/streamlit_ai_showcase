from openai import OpenAI
import streamlit as st
import os
import anthropic

# Set up the Streamlit application title
st.title("ChatGPT-like clone")

model_provider = st.selectbox(
    "Select model provider:",
    ("OpenAI", "Claude Anthropic", "Together AI")
)

# Initialize the client based on the selected model provider
if model_provider == "OpenAI":
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    st.session_state["model"] = "gpt-3.5-turbo"
elif model_provider == "Claude Anthropic":
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    st.session_state["model"] = "claude-2"
elif model_provider == "Together AI":
    client = OpenAI(api_key=os.getenv("TOGETHER_API_KEY"), base_url=os.getenv("TOGETHER_BASE_URL"))
    st.session_state["model"] = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Initialize the message history
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
        
        if model_provider == "Claude Anthropic":
            response = client.completions.create(
                model=st.session_state["model"],
                prompt=f"Human: {prompt}\n\nAssistant:",
                max_tokens_to_sample=300,
                stream=True
            )
            for chunk in response:
                full_response += (chunk.completion or "")
                message_placeholder.markdown(full_response + "▌")
        else:
            for response in client.chat.completions.create(
                model=st.session_state["model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # Append assistant's response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
