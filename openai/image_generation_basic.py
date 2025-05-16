#!/usr/bin/env python3
"""
Basic Image Generation with GPT Image API

This script demonstrates how to generate images using OpenAI's GPT Image API 
with basic parameters. This is the simplest approach for getting started with 
image generation.

Features:
- Generates a single image from a text prompt
- Saves the generated image to a file
- Configurable parameters for image quality, size, and format

Usage:
1. Set your OpenAI API key in your environment variables or in the script
2. Customize the prompt to describe the image you want to generate
3. Adjust parameters like quality, size, and format as needed
4. Run the script to generate and save the image

Requirements:
- Python 3.6+
- openai library (pip install openai)
- Pillow library (pip install Pillow)
"""

import base64
import os
from io import BytesIO
import argparse
from PIL import Image
from openai import OpenAI

def setup_client():
    """Initialize and return an OpenAI client"""
    # Try to get API key from environment, otherwise use a default value
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found! Set your API key as OPENAI_API_KEY environment variable."
        )
    
    return OpenAI(api_key=api_key)

def create_output_folder(folder_path="output_images"):
    """Create a folder to store generated images if it doesn't exist"""
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def generate_image(
    client, 
    prompt, 
    output_path,
    size="1024x1024", 
    quality="standard", 
    output_format="png",
    output_compression=80
):
    """
    Generate an image using GPT Image API
    
    Args:
        client: OpenAI client instance
        prompt: Text description of the image to generate
        output_path: Path to save the generated image
        size: Image dimensions as 'widthxheight'. Options: '1024x1024', '1024x1536', '1536x1024'
        quality: Image quality. Options: 'low', 'medium', 'high', 'auto'
        output_format: File format for the output image. Options: 'png', 'jpeg', 'webp'
        output_compression: Compression level for the output image (0-100, only for jpeg/webp)
    
    Returns:
        Path to the saved image
    """
    try:
        print(f"Generating image with prompt: '{prompt}'")
        print(f"Parameters: size={size}, quality={quality}, format={output_format}")
        
        # Call OpenAI API to generate the image
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            quality=quality,
            output_format=output_format,
        )
        
        # Extract and decode the image data
        image_data = result.data[0].b64_json
        image_bytes = base64.b64decode(image_data)
        
        # Open, resize, and save the image
        image = Image.open(BytesIO(image_bytes))
        
        # Save with appropriate format and compression
        if output_format == "jpeg":
            image.save(output_path, format="JPEG", quality=output_compression, optimize=True)
        elif output_format == "webp":
            image.save(output_path, format="WEBP", quality=output_compression)
        else:  # PNG or other formats
            image.save(output_path, format=output_format.upper())
        
        print(f"Image successfully saved to: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error generating image: {e}")
        raise

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate an image using OpenAI GPT Image API')
    parser.add_argument('--prompt', type=str, default="An elaborate steampunk city with floating airships, gears, and Victorian architecture in a sunset", 
                        help='Text description of the image to generate')
    parser.add_argument('--size', type=str, default="1024x1024", choices=["1024x1024", "1024x1536", "1536x1024"],
                        help='Image dimensions (widthxheight)')
    parser.add_argument('--quality', type=str, default="standard", choices=["low", "medium", "high", "auto"],
                        help='Image quality')
    parser.add_argument('--format', type=str, default="png", choices=["png", "jpeg", "webp"],
                        help='Output image format')
    parser.add_argument('--output', type=str, default="generated_image", 
                        help='Output filename (without extension)')
    args = parser.parse_args()
    
    # Setup
    client = setup_client()
    output_folder = create_output_folder()
    
    # Prepare output path with appropriate extension
    output_path = os.path.join(output_folder, f"{args.output}.{args.format}")
    
    # Generate the image
    generate_image(
        client, 
        args.prompt, 
        output_path,
        size=args.size, 
        quality=args.quality, 
        output_format=args.format
    )

if __name__ == "__main__":
    main()
