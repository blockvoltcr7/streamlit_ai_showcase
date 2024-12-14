import os
import time

import requests
import streamlit as st
from dotenv import load_dotenv
from lumaai import LumaAI

from openai import OpenAI


def initialize_clients():
    """Initialize Luma AI and OpenAI clients with API keys."""
    load_dotenv()

    # Initialize Luma AI
    luma_key = os.getenv("LUMAAI_API_KEY")
    if not luma_key:
        st.error("LUMAAI_API_KEY not found in environment variables")
        st.stop()
    luma_client = LumaAI(auth_token=luma_key)

    # Initialize OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        st.error("OPENAI_API_KEY not found in environment variables")
        st.stop()
    openai_client = OpenAI(api_key=openai_key)

    return luma_client, openai_client


def enhance_prompt(openai_client, original_prompt):
    """Enhance the user's prompt using OpenAI."""
    system_prompt = """You are an expert AI video prompt engineer specializing in text-to-video generation. 
    Your task is to enhance user prompts to create the most visually compelling and detailed video sequences.
    
    Consider these aspects when enhancing prompts:
    - Visual composition and scene details
    - Lighting and atmosphere
    - Camera movements and angles
    - Character or object descriptions
    - Action and motion
    - Style and artistic direction
    
    Provide your response in two parts:
    1. Enhanced prompt: The improved version ready for video generation
    2. Explanation: Brief explanation of your enhancements
    
    Format your response exactly as:
    ENHANCED_PROMPT: [Your enhanced prompt]
    EXPLANATION: [Your explanation]"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Original prompt: {original_prompt}\n\nPlease enhance this prompt for text-to-video generation.",
                },
            ],
            temperature=0.7,
        )

        response_text = response.choices[0].message.content

        # Split the response into prompt and explanation
        parts = response_text.split("EXPLANATION:")
        enhanced_prompt = parts[0].replace("ENHANCED_PROMPT:", "").strip()
        explanation = parts[1].strip() if len(parts) > 1 else "No explanation provided"

        return enhanced_prompt, explanation
    except Exception as e:
        st.error(f"Error enhancing prompt with OpenAI: {str(e)}")
        return None, None


def generate_video(client, prompt):
    """Generate video using Luma AI."""
    video_placeholder = st.empty()
    status_placeholder = st.empty()

    try:
        with status_placeholder.status("Generating video...", expanded=True) as status:
            generation = client.generations.create(prompt=prompt)

            while True:
                generation = client.generations.get(id=generation.id)
                if generation.state == "completed":
                    status.update(
                        label="Video generated successfully!", state="complete"
                    )
                    break
                elif generation.state == "failed":
                    status.update(
                        label=f"Generation failed: {generation.failure_reason}",
                        state="error",
                    )
                    st.error(f"Generation failed: {generation.failure_reason}")
                    return None
                status.write(f"Current status: {generation.state}...")
                time.sleep(3)

            # Download and display video automatically
            video_data, _ = download_video(generation.assets.video, generation.id)
            if video_data:
                video_placeholder.video(video_data)
                st.session_state.current_video = video_data
                st.session_state.current_generation = generation

            return generation

    except Exception as e:
        st.error(f"An error occurred during video generation: {str(e)}")
        return None


def download_video(video_url, generation_id):
    """Download the generated video."""
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Save video locally
        filename = f"{generation_id}.mp4"
        with open(filename, "wb") as file:
            file.write(response.content)

        # Read the file for download button
        with open(filename, "rb") as file:
            video_data = file.read()

        return video_data, filename
    except Exception as e:
        st.error(f"An error occurred while downloading the video: {str(e)}")
        return None, None


def main():
    st.title("🎬 AI Enhanced Video Generator")

    # Initialize session state for video display
    if "current_video" not in st.session_state:
        st.session_state.current_video = None
    if "current_generation" not in st.session_state:
        st.session_state.current_generation = None

    st.write(
        """
    Enter a prompt to generate a video using AI. Your prompt will be enhanced by an AI expert system 
    before being used to generate the video.
    """
    )

    # Initialize clients
    luma_client, openai_client = initialize_clients()

    # Create columns for the layout
    prompt_col, video_col = st.columns([1, 1])

    with prompt_col:
        # User input
        original_prompt = st.text_area(
            "Enter your prompt:",
            placeholder="Example: A teddy bear in sunglasses playing electric guitar and dancing",
            help="Describe what you want to see in the video",
        )

        if original_prompt:
            # Enhanced prompt generation
            if st.button("Enhance Prompt"):
                with st.spinner("Enhancing your prompt..."):
                    enhanced_prompt, explanation = enhance_prompt(
                        openai_client, original_prompt
                    )

                    if enhanced_prompt:
                        st.session_state.enhanced_prompt = enhanced_prompt
                        st.session_state.explanation = explanation

                        st.subheader("Enhanced Prompt")
                        st.write(enhanced_prompt)

                        with st.expander("See enhancement explanation"):
                            st.write(explanation)

            # Video generation
            if st.button("Generate Video", disabled=not original_prompt):
                prompt_to_use = st.session_state.get("enhanced_prompt", original_prompt)

                with st.spinner("Initializing video generation..."):
                    generation = generate_video(luma_client, prompt_to_use)

                    if generation:
                        st.session_state.current_generation = generation

    with video_col:
        # Display current video if available
        if st.session_state.current_video is not None:
            st.subheader("Generated Video")
            st.video(st.session_state.current_video)

            # Download button
            st.download_button(
                label="Download Video",
                data=st.session_state.current_video,
                file_name=f"{st.session_state.current_generation.id}.mp4",
                mime="video/mp4",
            )

            # Generation details
            with st.expander("Generation Details"):
                st.json(
                    {
                        "generation_id": st.session_state.current_generation.id,
                        "state": st.session_state.current_generation.state,
                        "created_at": str(
                            st.session_state.current_generation.created_at
                        ),
                        "original_prompt": original_prompt,
                        "enhanced_prompt": st.session_state.get(
                            "enhanced_prompt", "No enhancement used"
                        ),
                        "enhancement_explanation": st.session_state.get(
                            "explanation", "No explanation available"
                        ),
                    }
                )


if __name__ == "__main__":
    main()
