import base64
import os
import time
import uuid
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from lumaai import LumaAI
from PIL import Image

from openai import OpenAI

# Load environment variables
load_dotenv()


def initialize_clients():
    """Initialize Luma AI and OpenAI clients."""
    luma_key = os.getenv("LUMAAI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not luma_key or not openai_key:
        st.error("Missing required API keys. Please check your .env file.")
        st.stop()

    return LumaAI(auth_token=luma_key), OpenAI(api_key=openai_key)


def load_prompt_guide():
    """Load the Luma AI prompt guide."""
    guide_path = Path("prompts/luma_ai_system_prompt.md")

    if not guide_path.exists():
        return "Default prompt guide: Generate a detailed video prompt based on the image content."

    try:
        with guide_path.open("r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading prompt guide: {e}"


def encode_image_to_base64(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image_with_vision(client, image_path, prompt_guide):
    """Analyze image using OpenAI's vision model."""
    base64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are a video prompt expert. Analyze the image and create a detailed prompt for Luma AI video generation following this guide: {prompt_guide}",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Generate a video prompt based on this image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content


def save_uploaded_file(uploaded_file):
    """
    Save the uploaded file to a temporary directory and return the file path.

    Args:
        uploaded_file: Streamlit's UploadedFile object

    Returns:
        Path: Path to the saved file
    """
    # Create a temporary directory if it doesn't exist
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    # Generate a unique filename using UUID
    file_extension = Path(uploaded_file.name).suffix
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = temp_dir / filename

    # Save the file
    try:
        with file_path.open("wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None


def generate_video(luma_client, prompt, image_path):
    """
    Generate a video using Luma AI based on the prompt and image.

    Args:
        luma_client: LumaAI client instance
        prompt: str, the approved prompt for video generation
        image_path: Path, path to the source image

    Returns:
        Generation object from Luma AI or None if generation fails
    """
    try:
        # Validate and preprocess image
        img = Image.open(image_path)
        # Convert to RGB if necessary (handles PNG transparency)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Save as JPEG temporarily
        temp_jpg_path = Path(
            str(image_path).replace(image_path.suffix, "_converted.jpg")
        )
        img.save(temp_jpg_path, "JPEG", quality=95)

        # Convert image to base64
        image_base64 = encode_image_to_base64(temp_jpg_path)
        image_url = f"data:image/jpeg;base64,{image_base64}"

        # Clean up temporary file
        temp_jpg_path.unlink(missing_ok=True)

        # Create generation with validated image
        generation = luma_client.generations.create(
            prompt=prompt, keyframes={"frame0": {"type": "image", "url": image_url}}
        )

        status_placeholder = st.empty()
        while True:
            generation = luma_client.generations.get(id=generation.id)

            if generation.state == "completed":
                status_placeholder.success("Video generated successfully!")
                break
            elif generation.state == "failed":
                status_placeholder.error(
                    f"Generation failed: {generation.failure_reason}"
                )
                return None

            status_placeholder.info(f"Generation status: {generation.state}")
            time.sleep(3)

        return generation

    except Exception as e:
        st.error(f"Error generating video: {e}")
        return None


def download_video(video_url, generation_id):
    """
    Download the generated video from Luma AI.

    Args:
        video_url: str, URL of the generated video
        generation_id: str, ID of the generation

    Returns:
        tuple: (video_data, filename) or (None, None) if download fails
    """
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Get video data
        video_data = response.content
        filename = f"{generation_id}.mp4"

        return video_data, filename

    except Exception as e:
        st.error(f"Error downloading video: {e}")
        return None, None


def main():
    st.title("🎬 Luma Dream Machine")
    st.write("Upload an image to generate an AI video!")

    # Initialize session state for storing the generated prompt
    if "generated_prompt" not in st.session_state:
        st.session_state.generated_prompt = None
    if "prompt_approved" not in st.session_state:
        st.session_state.prompt_approved = False

    # Initialize clients
    luma_client, openai_client = initialize_clients()

    # Load prompt guide
    prompt_guide = load_prompt_guide()

    # File uploader
    uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        # Display uploaded image
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Save uploaded file
        image_path = save_uploaded_file(uploaded_file)

        # Analyze Image Button
        if not st.session_state.generated_prompt and st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                # Analyze image and generate prompt
                generated_prompt = analyze_image_with_vision(
                    openai_client, image_path, prompt_guide
                )
                if generated_prompt:
                    st.session_state.generated_prompt = generated_prompt
                    st.rerun()

        # Display and allow editing of the generated prompt
        if st.session_state.generated_prompt:
            st.subheader("Generated Prompt")
            edited_prompt = st.text_area(
                "Review and edit the prompt if needed:",
                value=st.session_state.generated_prompt,
                height=200,
                key="prompt_editor",
            )

            # Prompt approval button
            if st.button("Approve Prompt"):
                st.session_state.generated_prompt = edited_prompt
                st.session_state.prompt_approved = True
                st.success("Prompt approved! You can now generate the video.")
                st.rerun()

        # Generate Video button (only shown after prompt is approved)
        if st.session_state.prompt_approved:
            if st.button("Generate Video"):
                with st.spinner("Generating video..."):
                    generation = generate_video(
                        luma_client, st.session_state.generated_prompt, image_path
                    )

                    if generation:
                        # Download and display video
                        video_data, filename = download_video(
                            generation.assets.video, generation.id
                        )

                        if video_data:
                            with col2:
                                st.subheader("Generated Video")
                                st.video(video_data)

                                # Download button
                                st.download_button(
                                    label="Download Video",
                                    data=video_data,
                                    file_name=f"{generation.id}.mp4",
                                    mime="video/mp4",
                                )

                            # Display generation details
                            with st.expander("Generation Details"):
                                st.json(
                                    {
                                        "generation_id": generation.id,
                                        "state": generation.state,
                                        "created_at": str(generation.created_at),
                                        "prompt": st.session_state.generated_prompt,
                                    }
                                )

        # Reset button to start over
        if st.session_state.generated_prompt:
            if st.button("Start Over"):
                st.session_state.generated_prompt = None
                st.session_state.prompt_approved = False
                st.rerun()


if __name__ == "__main__":
    main()
