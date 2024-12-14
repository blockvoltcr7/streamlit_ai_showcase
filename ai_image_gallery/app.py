import streamlit as st
import random
from PIL import Image
import io
import os

# Page config
st.set_page_config(
    page_title="AI Image Gallery",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .stImage:hover {
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎨 AI Image Gallery")
st.markdown("""
Welcome to the AI Image Gallery! This is a showcase of AI-generated artwork.
Use the sidebar to customize your viewing experience and generate new images.
""")

# Sidebar controls
st.sidebar.header("Gallery Controls")
style_option = st.sidebar.selectbox(
    "Art Style",
    ["Digital Art", "Oil Painting", "Watercolor", "Pencil Sketch", "Abstract"]
)

theme_option = st.sidebar.selectbox(
    "Theme",
    ["Nature", "Urban", "Fantasy", "Space", "Abstract"]
)

# Main content area with tabs
tab1, tab2 = st.tabs(["Gallery", "About"])

with tab1:
    # Create columns for the gallery
    col1, col2, col2 = st.columns(3)
    
    # Placeholder for when we integrate real AI image generation
    st.info("This is a demo version. In a full implementation, this would connect to an AI image generation API like DALL-E or Stable Diffusion.")
    
    # Example gallery layout
    if st.button("Generate New Images"):
        st.success("In a full implementation, this would generate new AI images based on your selected style and theme!")

with tab2:
    st.header("About this Gallery")
    st.markdown("""
    This AI Image Gallery is a demonstration of how Streamlit can be used to create
    interactive web applications for AI-generated art. In a full implementation, this
    would connect to:
    
    - AI Image Generation APIs
    - Image Storage Solutions
    - User Authentication
    - Image Rating System
    
    Built with ❤️ using Streamlit
    """)

# Footer
st.markdown("---")
st.markdown("Created by Cascade AI Assistant | [GitHub](https://github.com)")
