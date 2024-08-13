import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=GROQ_API_KEY)

LLAMA3_70B = "llama3-70b-8192"

st.title("Groq Chatbot")

user_role = st.selectbox("Select your role:", ["user", "system"])
user_content = st.text_area("Enter your message:")

# Add input fields for max_tokens and temperature
max_tokens = st.number_input("Max Tokens", min_value=1, max_value=4096, value=1024, step=1)
temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1)

if st.button("Submit"):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": user_role, "content": user_content}
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=LLAMA3_70B,
        # Pass the parameters directly
        max_tokens=max_tokens, 
        temperature=temperature, 
        top_p=1, 
        stream=False,  # Disable streaming for a single output
        stop=None
    )

    response = chat_completion.choices[0].message.content
    st.markdown(f"**Assistant:** {response}", unsafe_allow_html=True)
