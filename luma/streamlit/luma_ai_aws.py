import logging
import os
import uuid
from io import BytesIO

import boto3
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class S3Uploader:
    def __init__(self):
        """Initialize S3 client with credentials from environment variables."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        self.BUCKET_NAME = "lumaai"

    def process_and_upload_image(self, image_file: BytesIO) -> str:
        """
        Process and upload an image to S3.
        Returns the public URL of the uploaded image.
        """
        try:
            # Reset file pointer
            image_file.seek(0)

            # Open and process image
            image = Image.open(image_file)

            # Convert to RGBA if needed
            if image.mode != "RGBA":
                image = image.convert("RGBA")

            # Create a new BytesIO object for the processed image
            processed_image = BytesIO()

            # Save as PNG
            image.save(processed_image, format="PNG", optimize=True)
            processed_image.seek(0)

            # Generate unique filename with .png extension
            unique_filename = f"{uuid.uuid4()}.png"

            # Upload to S3
            self.s3_client.upload_fileobj(
                processed_image,
                self.BUCKET_NAME,
                unique_filename,
                ExtraArgs={"ContentType": "image/png"},
            )

            # Generate public URL
            region = os.getenv("AWS_REGION", "us-east-2")
            url = f"https://{self.BUCKET_NAME}.s3.{region}.amazonaws.com/{unique_filename}"
            print(f"Successfully uploaded image: {url}")
            logger.info(f"Successfully uploaded image: {url}")
            return url

        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise


def main():
    st.title("🖼️ S3 Image Uploader for Luma AI")
    st.write("Upload images to prepare for Luma AI video generation")

    # Initialize uploader
    try:
        uploader = S3Uploader()
    except Exception as e:
        st.error(f"Failed to initialize S3 uploader: {str(e)}")
        st.stop()

    # Initialize session state for uploaded URLs
    if "uploaded_urls" not in st.session_state:
        st.session_state.uploaded_urls = []

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose image files",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        help="Select one or more images to upload",
    )

    if uploaded_files:
        # Create columns for image preview
        cols = st.columns(3)

        # Process each uploaded file
        for idx, uploaded_file in enumerate(uploaded_files):
            col_idx = idx % 3
            with cols[col_idx]:
                # Show image preview
                st.image(uploaded_file, caption=f"Image {idx + 1}")

                # Add upload button for each image
                if st.button(f"Upload Image {idx + 1}", key=f"upload_{idx}"):
                    try:
                        with st.spinner(f"Uploading image {idx + 1}..."):
                            # Process and upload image
                            image_bytes = BytesIO(uploaded_file.read())
                            url = uploader.process_and_upload_image(image_bytes)

                            # Store and display URL
                            st.session_state.uploaded_urls.append(url)
                            st.success("Upload successful!")
                            st.code(url)
                    except Exception as e:
                        st.error(f"Failed to upload image: {str(e)}")

    # Display all uploaded URLs
    if st.session_state.uploaded_urls:
        st.header("Uploaded Images")
        for idx, url in enumerate(st.session_state.uploaded_urls, 1):
            st.text_input(f"Image {idx} URL", value=url, key=f"url_{idx}")

        # Add clear button
        if st.button("Clear All URLs"):
            st.session_state.uploaded_urls = []
            st.rerun()

    # Add help section
    with st.expander("Help & Information"):
        st.markdown(
            """
        **How to use this uploader:**
        1. Select one or more image files using the file uploader
        2. Preview the images before uploading
        3. Click the upload button for each image you want to upload
        4. Copy the generated URLs to use with Luma AI
        
        **Notes:**
        - Images are automatically optimized before upload
        - All uploads are public to work with Luma AI
        - URLs are preserved during your session
        - You can clear all URLs using the 'Clear All URLs' button
        """
        )


if __name__ == "__main__":
    main()
