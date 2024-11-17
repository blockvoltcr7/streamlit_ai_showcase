import base64
import os
import time
import uuid
from io import BytesIO
from pathlib import Path

import boto3
import requests
import streamlit as st
from dotenv import load_dotenv
from lumaai import LumaAI
from PIL import Image

from openai import OpenAI

# Load environment variables
load_dotenv()

BUCKET_NAME = "lumaai"


def initialize_clients():
    """Initialize Luma AI and OpenAI clients."""
    luma_key = os.getenv("LUMAAI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    if not luma_key or not openai_key or not aws_access_key or not aws_secret_key:
        st.error(
            "Missing required API keys or AWS credentials. Please check your .env file."
        )
        st.stop()

    return (
        LumaAI(auth_token=luma_key),
        OpenAI(api_key=openai_key),
        boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        ),
    )


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


def analyze_image_with_vision(
    client,
    image_path,
    prompt_guide,
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=300,
):
    """Analyze image using OpenAI's vision model."""
    base64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model=model,
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
        temperature=temperature,
        max_tokens=max_tokens,
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


def encode_image_to_base64(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def upload_image_to_s3(s3_client, image_bytes: BytesIO) -> str:
    """
    Upload an image to the images folder in S3 and return the public URL.

    Args:
        s3_client: boto3 S3 client
        image_bytes: BytesIO object containing the image data

    Returns:
        str: Public URL of the uploaded image
    """
    try:
        # Reset file pointer
        image_bytes.seek(0)

        # Generate unique filename with .png extension and include the images/ prefix
        unique_filename = f"images/{uuid.uuid4()}.png"

        # Upload to S3 without ACL parameter
        s3_client.upload_fileobj(
            image_bytes,
            BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": "image/png"},
        )

        # Generate public URL
        region = os.getenv("AWS_REGION", "us-east-2")
        url = f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{unique_filename}"
        print(f"Successfully uploaded image to: {url}")
        return url

    except Exception as e:
        st.error(f"Error uploading image to S3: {str(e)}")
        st.error(f"Bucket: {BUCKET_NAME}")
        st.error(f"Path: {unique_filename}")
        raise


def upload_video_to_s3(s3_client, video_bytes: BytesIO, generation_id: str) -> str:
    """
    Upload a video to the "videos" folder in the "lumaai" S3 bucket and return the public URL.

    Args:
        s3_client: boto3 S3 client
        video_bytes: BytesIO object containing the video data
        generation_id: str, ID of the generation

    Returns:
        str: Public URL of the uploaded video
    """
    try:
        # Reset file pointer
        video_bytes.seek(0)

        # Upload to S3
        s3_client.upload_fileobj(
            video_bytes,
            "lumaai",
            f"videos/{generation_id}.mp4",
            ExtraArgs={"ContentType": "video/mp4"},
        )

        # Generate public URL
        region = os.getenv("AWS_REGION", "us-east-2")
        url = f"https://lumaai.s3.{region}.amazonaws.com/videos/{generation_id}.mp4"
        print(f"Successfully uploaded video: {url}")
        return url

    except Exception as e:
        st.error(f"Error uploading video to S3: {str(e)}")
        raise


def generate_video(luma_client, prompt, image_url):
    """
    Generate a video using Luma AI based on the prompt and image.

    Args:
        luma_client: LumaAI client instance
        prompt: str, the approved prompt for video generation
        image_url: str, the public URL of the source image

    Returns:
        Generation object from Luma AI or None if generation fails
    """
    try:
        # Create generation with image URL
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
        BytesIO: Video data as BytesIO object, or None if download fails
    """
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Convert video data to BytesIO
        video_bytes = BytesIO(response.content)
        return video_bytes

    except Exception as e:
        st.error(f"Error downloading video: {e}")
        return None


def cleanup_temp_files(file_path=None):
    """
    Clean up temporary files.

    Args:
        file_path: Optional specific file to delete. If None, cleans entire temp directory.
    """
    try:
        if file_path:
            # Delete specific file
            if Path(file_path).exists():
                Path(file_path).unlink()
                print(f"Cleaned up temporary file: {file_path}")
        else:
            # Clean entire temp directory
            temp_dir = Path("temp")
            if temp_dir.exists():
                for file in temp_dir.glob("*"):
                    file.unlink()
                print("Cleaned up all temporary files")
    except Exception as e:
        print(f"Error cleaning up temporary files: {e}")


# Add the sidebar model selection function
def sidebar_model_selection():
    """Add model selection sidebar."""
    st.sidebar.header("Model Settings")

    # Model selection
    model = st.sidebar.selectbox(
        "Choose Vision Model:",
        ["gpt-4o", "gpt-4o-mini"],
        help="Select the model to use for image analysis",
    )

    # Add temperature parameter
    temperature = st.sidebar.slider(
        "Temperature:",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        help="Controls randomness in the output. Higher values make the output more creative.",
    )

    # Add max tokens parameter
    max_tokens = st.sidebar.slider(
        "Max Tokens:",
        min_value=100,
        max_value=500,
        value=300,
        help="Maximum number of tokens in the response.",
    )

    return model, temperature, max_tokens


def main():
    st.title("🎬 Luma Dream Machine")
    st.write("Upload an image to generate an AI video!")

    # Add model selection sidebar
    model, temperature, max_tokens = sidebar_model_selection()

    # Initialize session state for storing the generated prompt
    if "generated_prompt" not in st.session_state:
        st.session_state.generated_prompt = None
    if "prompt_approved" not in st.session_state:
        st.session_state.prompt_approved = False
    if "uploaded_image_url" not in st.session_state:
        st.session_state.uploaded_image_url = None

    # Initialize clients
    luma_client, openai_client, s3_client = initialize_clients()

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
                # Analyze image and generate prompt with selected model parameters
                generated_prompt = analyze_image_with_vision(
                    openai_client,
                    image_path,
                    prompt_guide,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
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

        # Upload Image to S3 and Generate Video button (only shown after prompt is approved)
        if st.session_state.prompt_approved:
            if st.button("Upload Image and Generate Video"):
                with st.spinner("Uploading image to S3 and generating video..."):
                    try:
                        # Upload image to S3 and get the URL
                        with open(image_path, "rb") as image_file:
                            image_bytes = BytesIO(image_file.read())
                        st.session_state.uploaded_image_url = upload_image_to_s3(
                            s3_client, image_bytes
                        )

                        # Clean up the temporary image file after successful upload
                        cleanup_temp_files(image_path)

                        # Generate video
                        generation = generate_video(
                            luma_client,
                            st.session_state.generated_prompt,
                            st.session_state.uploaded_image_url,
                        )

                        if generation:
                            # Download and display video
                            video_bytes = download_video(
                                generation.assets.video, generation.id
                            )

                            if video_bytes:
                                # Upload video to S3
                                video_url = upload_video_to_s3(
                                    s3_client, video_bytes, generation.id
                                )

                                with col2:
                                    st.subheader("Generated Video")
                                    # Display video using the S3 URL
                                    st.video(video_url)

                                    # Create a new BytesIO object for download
                                    download_video_bytes = download_video(
                                        generation.assets.video, generation.id
                                    )
                                    if download_video_bytes:
                                        st.download_button(
                                            label="Download Video",
                                            data=download_video_bytes,
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
                                            "image_url": st.session_state.uploaded_image_url,
                                            "video_url": video_url,
                                        }
                                    )
                    finally:
                        # Clean up any remaining temporary files
                        cleanup_temp_files()

        # Reset button to start over
        if st.session_state.generated_prompt or st.session_state.uploaded_image_url:
            if st.button("Start Over"):
                st.session_state.generated_prompt = None
                st.session_state.prompt_approved = False
                st.session_state.uploaded_image_url = None
                st.rerun()


if __name__ == "__main__":
    main()
