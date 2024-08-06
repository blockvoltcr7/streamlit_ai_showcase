import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

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
    tip1 = "Select a model you want to use."
    model = st.sidebar.radio("Choose LLM:",
                             ("gemini-1.5-flash",
                              "gemini-1.5-pro",
                              ), help=tip1)
    tip2 = "Lower temperatures lead to less random responses, higher temperatures to more diverse results."
    temp = st.sidebar.slider("Temperature:", min_value=0.0,
                             max_value=2.0, value=1.0, step=0.25, help=tip2)
    tip3 = "Used for nucleus sampling. Lower value for less random responses, higher for more random."
    topp = st.sidebar.slider("Top P:", min_value=0.0,
                             max_value=1.0, value=0.94, step=0.01, help=tip3)
    tip4 = "Number of response tokens, 8194 is limit."
    maxtokens = st.sidebar.slider("Maximum Tokens:", min_value=100,
                                  max_value=8194, value=2000, step=100, help=tip4)
    return model, temp, topp, maxtokens

def process_text(user_input, gemini_model, temperature, top_p, max_tokens):
    try:
        response = gemini_model.generate_content(
            user_input,
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
            }
        )
        return response
    except Exception as e:
        st.error(f"An error occurred while processing text: {str(e)}")
        return None

def process_image(image_file, prompt, gemini_model, temperature, top_p, max_tokens):
    try:
        # Save the uploaded file temporarily
        with open(image_file.name, "wb") as f:
            f.write(image_file.getbuffer())

        # Upload the image to Gemini
        uploaded_image = genai.upload_file(path=image_file.name)

        # Wait for processing
        while uploaded_image.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_image = genai.get_file(uploaded_image.name)

        if uploaded_image.state.name == "FAILED":
            raise ValueError("Image processing failed")

        # Generate content
        response = gemini_model.generate_content(
            [uploaded_image, prompt],
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
            },
            request_options={"timeout": 120}
        )

        # Delete the uploaded file
        os.remove(image_file.name)
        genai.delete_file(uploaded_image.name)

        return response
    except Exception as e:
        st.error(f"An error occurred while processing the image: {str(e)}")
        if os.path.exists(image_file.name):
            os.remove(image_file.name)
        return None

def main():
    page_setup()
    model, temperature, top_p, max_tokens = get_llminfo()

    # Configure Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        st.error("GEMINI_API_KEY environment variable is not set")
        return
    genai.configure(api_key=GEMINI_API_KEY)

    # Create Gemini model
    gemini_model = genai.GenerativeModel(model_name=model)

    # Input selection
    input_type = st.radio("Choose input type:", ("Text", "Image"))

    if input_type == "Text":
        user_input = st.text_area("Enter your text here:", height=150)
        if st.button("Submit Text"):
            if user_input:
                response = process_text(user_input, gemini_model, temperature, top_p, max_tokens)
                if response and response.parts:
                    st.markdown("### Response:")
                    st.markdown(response.text)
                elif response:
                    st.warning("Content generation was blocked or no valid content was generated.")
            else:
                st.warning("Please enter some text before submitting.")

    else:  # Image input
        uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
        prompt = st.text_input("Enter a prompt for the image:")
        
        if st.button("Process Image"):
            if uploaded_file is not None and prompt:
                response = process_image(uploaded_file, prompt, gemini_model, temperature, top_p, max_tokens)
                if response and response.parts:
                    st.markdown("### Response:")
                    st.markdown(response.text)
                elif response:
                    st.warning("Content generation was blocked or no valid content was generated.")
            else:
                st.warning("Please upload an image and enter a prompt before processing.")
                 # Add a checkbox for auto-refresh
    auto_refresh = st.sidebar.checkbox("Enable auto-refresh")

    if auto_refresh:
        # Add a placeholder for the timer
        timer_placeholder = st.empty()
        refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 5, 60, 30)
        
        # Count down to next refresh
        for remaining in range(refresh_interval, 0, -1):
            timer_placeholder.text(f"Refreshing in {remaining} seconds...")
            time.sleep(1)
        
        # Rerun the app
        st.rerun()

if __name__ == '__main__':
    main()