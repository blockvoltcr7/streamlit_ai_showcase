import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from io import BytesIO
import json
import tiktoken
from streamlit_float import *
from datetime import datetime

# Load environment variables
load_dotenv()

def page_setup():
    st.header("Chat with Gemini!", anchor=False, divider="blue")
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def get_llminfo():
    st.sidebar.header("Options", divider='rainbow')
    model = st.sidebar.radio("Choose LLM:", ("gemini-1.5-flash", "gemini-1.5-pro"))
    temp = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=1.0, step=0.25)
    topp = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=0.94, step=0.01)
    maxtokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=8194, value=2000, step=100)
    return model, temp, topp, maxtokens

def process_image(image_file, prompt, gemini_model, temperature, top_p, max_tokens):
    try:
        with open(image_file.name, "wb") as f:
            f.write(image_file.getbuffer())
        uploaded_image = genai.upload_file(path=image_file.name)
        while uploaded_image.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_image = genai.get_file(uploaded_image.name)
        if uploaded_image.state.name == "FAILED":
            raise ValueError("Image processing failed")
        response = gemini_model.generate_content(
            [uploaded_image, prompt],
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
            },
            request_options={"timeout": 120}
        )
        os.remove(image_file.name)
        genai.delete_file(uploaded_image.name)
        return response
    except Exception as e:
        st.error(f"An error occurred while processing the image: {str(e)}")
        if os.path.exists(image_file.name):
            os.remove(image_file.name)
        return None

@st.experimental_dialog("🎨 Upload a picture")
def upload_document():
    st.warning(
        "This is a demo dialog window. You need to process the file afterwards.",
        icon="💡",
    )
    picture = st.file_uploader(
        "Choose a file", type=["png", "jpg", "jpeg"], label_visibility="hidden"
    )
    if picture:
        st.session_state["uploaded_pic"] = picture
        st.rerun()
    

def main():
    page_setup()
    model, temperature, top_p, max_tokens = get_llminfo()

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        st.error("GEMINI_API_KEY environment variable is not set")
        return
    genai.configure(api_key=GEMINI_API_KEY)

    gemini_model = genai.GenerativeModel(model_name=model)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False

    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
    prompt = st.text_input("Enter a prompt for the image:")
    if st.button("Process Image"):
        if uploaded_file is not None and prompt:
            response = process_image(uploaded_file, prompt, gemini_model, temperature, top_p, max_tokens)
            if response and response.parts:
                st.markdown("### Response:")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "user", "content": f"[Image uploaded] {prompt}"})
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.session_state.chat_started = True
            elif response:
                st.warning("Content generation was blocked or no valid content was generated.")
        else:
            st.warning("Please upload an image and enter a prompt before processing.")

  # Chat interface after initial query
    if st.session_state.chat_started:
        st.markdown("### Continue the conversation:")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_input = st.chat_input("Ask a follow-up question:")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            if "current_image" in st.session_state and st.session_state.current_image is not None:
                # Process with image context
                response = process_image_with_context(
                    uploaded_file, 
                    prompt,
                    st.session_state.messages,
                    gemini_model, 
                    temperature, 
                    top_p, 
                    max_tokens
                )
            else:
                # Process without image context
                response = process_text(user_input, gemini_model, temperature, top_p, max_tokens)

            if response and response.parts:
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                with st.chat_message("assistant"):
                    st.markdown(response.text)
            else:
                st.warning("No valid response generated.")

        
  # Action buttons
    if len(st.session_state.messages) > 0:
        action_buttons_container = st.container()
        action_buttons_container.float(
            "bottom: 6.9rem;background-color: var(--default-backgroundColor); padding-top: 1rem;"
        )

        # We set the space between the icons thanks to a share of 100
        cols_dimensions = [5, 22, 22, 22, 22]
        cols_dimensions.append(100 - sum(cols_dimensions))

        col0, col1, col2, col3, col4, col5 = action_buttons_container.columns(cols_dimensions)

        with col1:
            json_messages = json.dumps(st.session_state.messages).encode("utf-8")
            st.download_button(
                label="📥 Save!",
                data=json_messages,
                file_name="chat_conversation.json",
                mime="application/json",
            )

        with col2:
            enc = tiktoken.get_encoding("cl100k_base")
            tokenized_full_text = enc.encode(" ".join([item["content"] for item in st.session_state.messages]))
            label = f"💬 {len(tokenized_full_text)} tokens"
            st.link_button(label, "https://platform.openai.com/tokenizer")

        with col3:
            if st.button("🧹 Clear Chat"):
                st.session_state.messages = []
                st.session_state.chat_started = False
                st.rerun()

        with col4:
            if st.button("🎨 upload img"):
                upload_document()

    if "uploaded_pic" in st.session_state:
        uploaded_file = st.session_state["uploaded_pic"]
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        prompt = st.text_input("Enter a prompt for the image:", key="image_prompt")
        if st.button("Process Image"):
            if prompt:
                image_response = process_image_with_context(
                    uploaded_file, 
                    prompt,
                    st.session_state.messages,
                    gemini_model, 
                    temperature, 
                    top_p, 
                    max_tokens
                )
                if image_response and image_response.parts:
                    st.session_state.messages.append({"role": "user", "content": f"[Image uploaded] {prompt}"})
                    st.session_state.messages.append({"role": "assistant", "content": image_response.text})
                    with st.chat_message("assistant"):
                        st.markdown(image_response.text)
                    st.success("Image processed and added to the conversation.")
                    st.session_state.current_image = uploaded_file.getvalue()  # Store the image data
                    del st.session_state["uploaded_pic"]
                    st.rerun()
                else:
                    st.error("Failed to process the image. Please try again.")
            else:
                st.warning("Please enter a prompt for the image.")

    # Auto-refresh feature
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh")
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 5, 60, 30)
        timer_placeholder = st.sidebar.empty()
        for remaining in range(refresh_interval, 0, -1):
            timer_placeholder.text(f"Refreshing in {remaining} seconds...")
            time.sleep(1)
        st.rerun()

if __name__ == '__main__':
    main()
