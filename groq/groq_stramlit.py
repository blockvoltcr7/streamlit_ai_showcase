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

if st.button("Submit"):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": user_role, "content": user_content}
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=LLAMA3_70B,
    )

    response = chat_completion.choices[0].message.content
    st.markdown(f"**Assistant:** {response}")
