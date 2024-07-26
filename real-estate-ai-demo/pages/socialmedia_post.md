# Social Media Post Generator for Real Estate Listings

## Overview

This Python script automates the creation of engaging Facebook posts for real estate listings. It uses the OpenAI API to generate compelling text based on property details and images. The script features a Streamlit web interface, making it easy for users to input property information and receive a ready-to-publish Facebook post.

## Features

- **Concurrent Image Processing**: Efficiently downloads and processes multiple property images.
- **Image Grid Creation**: Combines multiple property images into a single, visually appealing grid.
- **AI-Powered Content Generation**: Utilizes OpenAI's API to create informative and engaging post content.
- **User-Friendly Interface**: Streamlit-based web application for easy input and output.

## Key Functions

- `get_image(url)`: Downloads an image from a given URL.
- `download_images_concurrently(image_urls)`: Fetches multiple images in parallel for improved performance.
- `create_image_grid(image_urls, grid_max_width=4)`: Arranges downloaded images into a grid format.
- `encode_image(image)`: Converts a PIL Image object to a base64 string for easy handling.

## How to Use

1. **Setup**:
   - Ensure Python is installed on your system.
   - Install required libraries: `pip install streamlit openai requests Pillow`
   - Set up your OpenAI API key securely (use Streamlit secrets or environment variables).

2. **Running the Application**:
   - Execute the script: `streamlit run 1_SOCIALMEDIA_POST.PY`
   - The Streamlit interface will open in your default web browser.

3. **Using the Interface**:
   - Enter property details (address, community name, municipality, house type, description).
   - Provide URLs for property images.
   - Click "Generate Facebook Post" to create your social media content.

## Requirements

- Python 3.x
- Streamlit
- OpenAI Python library
- Requests
- Pillow (PIL)
- concurrent.futures (standard library)

## Security Note

Ensure that your OpenAI API key is stored securely and not exposed in your source code.

## Conclusion

This tool streamlines the process of creating professional, AI-generated social media content for real estate listings. It's designed to save time and enhance the quality of property marketing on platforms like Facebook.