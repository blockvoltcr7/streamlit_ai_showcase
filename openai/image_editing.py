#!/usr/bin/env python3
"""
Image Editing with GPT Image API

This script demonstrates how to use the OpenAI GPT Image API to edit existing
images or combine multiple images with a text prompt.

Features:
- Edit existing images with text prompts
- Combine multiple images into a single composition
- Create masks to protect parts of an image during editing
- Support for transparency and various output formats

Usage:
1. Set your OpenAI API key in environment variables
2. Provide one or more input images
3. Specify a prompt describing the desired edits
4. Optionally provide or generate a mask to protect parts of the image
5. Run the script to generate the edited image

Requirements:
- Python 3.6+
- openai library (pip install openai)
- Pillow library (pip install Pillow)
"""

import base64
import os
import time
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

def open_image(image_path):
    """Open an image file and return it"""
    try:
        with open(image_path, "rb") as img_file:
            return img_file.read()
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        raise

def generate_mask(client, img_input, output_path, mask_prompt=None):
    """
    Generate a mask for an image using GPT Image API
    
    Args:
        client: OpenAI client instance
        img_input: Input image bytes
        output_path: Path to save the generated mask
        mask_prompt: Prompt to guide mask generation, defaults to a standard mask prompt
        
    Returns:
        Path to the saved mask image
    """
    if mask_prompt is None:
        mask_prompt = "Generate a mask delimiting the main subject/character in the picture. Use white for the subject and black for the background. Return an image with the same dimensions as the input."
    
    try:
        print("Generating mask with prompt:", mask_prompt)
        
        # Call OpenAI API to generate the mask
        result_mask = client.images.edit(
            model="gpt-image-1",
            image=img_input,
            prompt=mask_prompt
        )
        
        # Extract and decode the mask data
        image_base64 = result_mask.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Open and save the mask
        mask = Image.open(BytesIO(image_bytes))
        mask.save(output_path, format="PNG")
        
        print(f"Mask successfully saved to: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error generating mask: {e}")
        raise

def convert_mask_to_alpha(mask_path, alpha_mask_path):
    """
    Convert a black and white mask to an RGBA image with alpha channel
    
    Args:
        mask_path: Path to the black and white mask image
        alpha_mask_path: Path to save the RGBA mask with alpha channel
        
    Returns:
        Path to the saved alpha mask
    """
    try:
        # Load the mask as grayscale
        mask = Image.open(mask_path).convert("L")
        
        # Convert to RGBA with alpha channel
        mask_rgba = mask.convert("RGBA")
        
        # Use the mask as the alpha channel
        mask_rgba.putalpha(mask)
        
        # Save the mask with alpha channel
        mask_rgba.save(alpha_mask_path, format="PNG")
        
        print(f"Alpha mask successfully saved to: {alpha_mask_path}")
        return alpha_mask_path
    
    except Exception as e:
        print(f"Error converting mask to alpha: {e}")
        raise

def edit_image(
    client,
    input_images,
    prompt,
    output_path,
    mask=None,
    size="1024x1024",
    quality="high",
    output_format="png"
):
    """
    Edit images using GPT Image API
    
    Args:
        client: OpenAI client instance
        input_images: List of input image file paths or bytes objects
        prompt: Text description of the desired edit
        output_path: Path to save the edited image
        mask: Optional mask image to protect parts of the first input image
        size: Image dimensions as 'widthxheight'
        quality: Image quality
        output_format: File format for the output image
        
    Returns:
        Path to the saved edited image
    """
    try:
        print(f"Editing image with prompt: '{prompt}'")
        
        # Prepare input images
        images = []
        for img in input_images:
            if isinstance(img, str):
                images.append(open_image(img))
            else:
                images.append(img)
        
        # Call OpenAI API to edit the image
        if mask:
            result_edit = client.images.edit(
                model="gpt-image-1",
                image=images[0],  # First image
                mask=mask,        # Mask applies to first image only
                prompt=prompt,
                size=size,
                quality=quality
            )
        elif len(images) > 1:
            # If multiple images without mask, use them all
            result_edit = client.images.edit(
                model="gpt-image-1",
                image=images,
                prompt=prompt,
                size=size,
                quality=quality
            )
        else:
            # Single image without mask
            result_edit = client.images.edit(
                model="gpt-image-1",
                image=images[0],
                prompt=prompt,
                size=size,
                quality=quality
            )
        
        # Extract and decode the edited image data
        image_base64 = result_edit.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Open and save the edited image
        image = Image.open(BytesIO(image_bytes))
        
        # Save with appropriate format
        if output_format == "jpeg":
            image.save(output_path, format="JPEG", quality=90, optimize=True)
        elif output_format == "webp":
            image.save(output_path, format="WEBP", quality=90)
        else:  # PNG or other formats
            image.save(output_path, format=output_format.upper())
        
        print(f"Edited image successfully saved to: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error editing image: {e}")
        raise

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Edit images using OpenAI GPT Image API')
    parser.add_argument('--input', type=str, required=True, nargs='+',
                        help='Input image file path(s)')
    parser.add_argument('--prompt', type=str, required=True,
                        help='Text description of the desired edit')
    parser.add_argument('--output', type=str, default="edited_image",
                        help='Output filename (without extension)')
    parser.add_argument('--generate-mask', action='store_true',
                        help='Generate a mask for the first input image')
    parser.add_argument('--mask-prompt', type=str,
                        help='Custom prompt for mask generation')
    parser.add_argument('--mask', type=str,
                        help='Path to existing mask image')
    parser.add_argument('--size', type=str, default="1024x1024", 
                       choices=["1024x1024", "1024x1536", "1536x1024"],
                       help='Image dimensions (widthxheight)')
    parser.add_argument('--quality', type=str, default="high", 
                       choices=["low", "medium", "high", "auto"],
                       help='Image quality')
    parser.add_argument('--format', type=str, default="png", 
                       choices=["png", "jpeg", "webp"],
                       help='Output image format')
    args = parser.parse_args()
    
    # Setup
    client = setup_client()
    output_folder = create_output_folder()
    timestamp = int(time.time())
    
    # Prepare mask if needed
    mask_bytes = None
    if args.generate_mask:
        # Generate a mask for the first input image
        first_img_bytes = open_image(args.input[0])
        mask_path = os.path.join(output_folder, f"mask_{timestamp}.png")
        alpha_mask_path = os.path.join(output_folder, f"mask_alpha_{timestamp}.png")
        
        # Generate mask using GPT Image
        generate_mask(client, first_img_bytes, mask_path, args.mask_prompt)
        
        # Convert to alpha mask
        convert_mask_to_alpha(mask_path, alpha_mask_path)
        
        # Read the alpha mask
        mask_bytes = open_image(alpha_mask_path)
    elif args.mask:
        # Use provided mask
        mask_bytes = open_image(args.mask)
    
    # Prepare output path
    output_path = os.path.join(output_folder, f"{args.output}_{timestamp}.{args.format}")
    
    # Edit the image
    edit_image(
        client,
        args.input,
        args.prompt,
        output_path,
        mask=mask_bytes,
        size=args.size,
        quality=args.quality,
        output_format=args.format
    )

if __name__ == "__main__":
    main()
