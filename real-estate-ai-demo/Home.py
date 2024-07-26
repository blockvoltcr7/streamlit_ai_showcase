# Import necessary libraries
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

# Page title and description
st.title("Real Estate Social Media Automation SaaS")
st.write("Welcome to our platform that simplifies social media management for real estate professionals!")

# Feature 1: Facebook Post Automation
st.header("1. Facebook Post Automation")
st.write("Effortlessly schedule and automate your real estate listings, updates, and engaging content on Facebook. Save time and maintain a consistent online presence by planning your posts in advance. Our intuitive interface makes it easy to customize posting schedules and target specific audiences for maximum impact.")

# Feature 2: TikTok Video Automation
st.header("2. TikTok Video Automation")
st.write("Tap into the power of TikTok to showcase your real estate properties through engaging videos. Our platform allows you to automate the creation and scheduling of TikTok videos, ensuring that your listings stand out in the ever-growing TikTok community. Enhance your marketing strategy with dynamic, visually appealing content that captures the attention of potential buyers.")

# Feature 3: SEO Image Alt Text Generator
st.header("3. SEO Image Alt Text Generator")
st.write("Boost the search engine visibility of your real estate listings with our SEO Image Alt Text Generator. Automatically generate descriptive and keyword-rich alt text for your property images. This feature not only enhances accessibility for users with disabilities but also contributes to better SEO rankings. Improve the discoverability of your listings and drive more traffic to your real estate website.")

# Add any additional features or details here...

# Conclusion or Call to Action
st.write("Take your real estate social media strategy to the next level with our all-in-one automation platform. Sign up today and experience the convenience of managing your online presence effortlessly.")

with open("tiktok_video_with_text.mp4", 'rb') as v:
    st.video(v)