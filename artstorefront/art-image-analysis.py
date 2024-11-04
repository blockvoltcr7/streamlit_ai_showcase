import base64
import os
import random
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st
from pydantic import BaseModel

from openai import OpenAI


class ImageAnalysisState(BaseModel):
    """State representation for image analysis."""

    image_path: str = ""
    image_exists: bool = False
    base64_image: str = ""
    analysis_result: str = ""
    error_message: Optional[str] = None
    media_recommendation: Optional[str] = None


def encode_image(image_path: str) -> str:
    """Encode the image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf8")


def analyze_image(base64_image: str, analysis_prompt: str, client: OpenAI) -> str:
    """Analyze the image using OpenAI's API."""
    try:
        response = client.chat.completions.create(
            model=st.session_state.selected_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=st.session_state.max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return ""


def generate_media_recommendations(analysis_result: str, client: OpenAI) -> str:
    """Generate media recommendations based on analysis."""
    media_options = st.session_state.media_prompt
    media_prompt = f"""
        based on the following details of the image {analysis_result}
        You are a Print Media Specialist tasked with recommending optimal print media for a given artwork. Please choose 4 media types from the options below based on their characteristics and suitability for vibrant color reproductions and artistic effects.

        {media_options}
  
        finally act as an expert artist and social media expert then create a title, description, short description, social media description, and catalog description
        """

    try:
        response = client.chat.completions.create(
            model=st.session_state.selected_model,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": media_prompt}],
                }
            ],
            max_tokens=st.session_state.max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return ""


def save_results(analysis_result: str, media_recommendation: str) -> tuple:
    """Save results to files and return filenames."""
    os.makedirs("output", exist_ok=True)
    random_number = random.randint(1000, 9999)

    analysis_filename = f"output/image_analysis_{random_number}.md"
    media_filename = f"output/media_recommendation_{random_number}.md"

    with open(analysis_filename, "w") as file:
        file.write("# Image Analysis Results\n\n")
        file.write(f"{analysis_result}\n\n")

    with open(media_filename, "w") as file:
        file.write("# Media Recommendation\n\n")
        file.write(f"{media_recommendation}\n\n")

    return analysis_filename, media_filename


def read_prompt_file(filename: str) -> str:
    """Read the content of a prompt file from the prompts directory."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(root_dir, "prompts", filename)

    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"Error: The file '{filename}' was not found.")
        return ""


def initialize_session_state():
    """Initialize session state variables with default values."""
    if "analysis_prompt" not in st.session_state:
        st.session_state.analysis_prompt = read_prompt_file("describe-image.md")

    if "media_prompt" not in st.session_state:
        st.session_state.media_prompt = read_prompt_file("media_prompt.md")

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gpt-4"

    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 4096


def main():
    st.title("AI Image Analysis System")

    # Initialize session state
    initialize_session_state()

    # Sidebar for configurations
    with st.sidebar:
        st.header("Configuration")
        st.session_state.selected_model = st.selectbox(
            "Select Model",
            ["gpt-4o", "gpt-4o-mini"],
            help="Choose the OpenAI model to use for analysis",
        )

        st.session_state.max_tokens = st.slider(
            "Max Tokens",
            min_value=1000,
            max_value=8192,
            value=4096,
            help="Maximum number of tokens for the response",
        )

    # Main content area
    st.header("Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image file", type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Create tabs for different sections
        prompt_tab, analysis_tab, media_tab = st.tabs(
            ["Customize Prompts", "Image Analysis", "Media Recommendations"]
        )

        with prompt_tab:
            st.subheader("Analysis Prompt")
            st.session_state.analysis_prompt = st.text_area(
                "Customize the analysis prompt:",
                value=st.session_state.analysis_prompt,
                height=300,
            )

            st.subheader("Media Recommendation Prompt")
            st.session_state.media_prompt = st.text_area(
                "Customize the media recommendation prompt:",
                value=st.session_state.media_prompt,
                height=300,
            )

        # Analysis section
        with analysis_tab:
            if st.button("Analyze Image"):
                with st.spinner("Analyzing image..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".jpg"
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name

                    # Initialize OpenAI client
                    client = OpenAI()

                    # Encode and analyze image
                    base64_img = encode_image(temp_path)
                    analysis_result = analyze_image(
                        base64_img, st.session_state.analysis_prompt, client
                    )

                    if analysis_result:
                        st.session_state.analysis_result = analysis_result
                        st.markdown("### Analysis Results")
                        st.text_area("Analysis Output", analysis_result, height=400)

                    # Clean up temporary file
                    os.unlink(temp_path)

        # Media recommendations section
        with media_tab:
            if st.button("Generate Media Recommendations"):
                if hasattr(st.session_state, "analysis_result"):
                    with st.spinner("Generating media recommendations..."):
                        client = OpenAI()
                        media_recommendation = generate_media_recommendations(
                            st.session_state.analysis_result, client
                        )

                        if media_recommendation:
                            st.session_state.media_recommendation = media_recommendation
                            st.markdown("### Media Recommendations")
                            st.text_area(
                                "Recommendations Output",
                                media_recommendation,
                                height=400,
                            )
                else:
                    st.warning(
                        "Please analyze the image first before generating media recommendations."
                    )

        # Save results
        if hasattr(st.session_state, "analysis_result") and hasattr(
            st.session_state, "media_recommendation"
        ):
            if st.button("Save Results"):
                analysis_file, media_file = save_results(
                    st.session_state.analysis_result,
                    st.session_state.media_recommendation,
                )
                st.success(
                    f"""Results saved successfully!
                Analysis: {analysis_file}
                Media Recommendations: {media_file}"""
                )


if __name__ == "__main__":
    main()
