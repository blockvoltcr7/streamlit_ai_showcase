import streamlit as st
import os

# Define file paths
image_path = os.path.join('..','images', 'angelic_warrior.png')
audio_path = os.path.join('..', 'audio', 'bf05d57b-b3d3-4b1f-a257-651721b25973.mp3')
video_path = 'path_to_your_video_file.mp4'  # Replace with your actual video file path

def main():
    st.title("Streamlit Media Display Demo")

    # Display image
    if os.path.exists(image_path):
        st.image(image_path, caption='Angelic Warrior')
    else:
        st.error(f"Image file not found: {image_path}")

    # Play audio
    if os.path.exists(audio_path):
        st.audio(audio_path, format='audio/mp3')
    else:
        st.error(f"Audio file not found: {audio_path}")

    # Display video
    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.error(f"Video file not found: {video_path}")

if __name__ == "__main__":
    main()