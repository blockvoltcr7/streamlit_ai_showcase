#!/usr/bin/env python3
"""
Advanced Image Generation with GPT Image API

This script demonstrates advanced features of the OpenAI GPT Image API,
including detailed character descriptions and customizing output properties.

Features:
- Complex character/scene description generation
- Full control over image quality, size, format and compression
- Customizable output settings
- Output file naming based on content

Usage:
1. Set your OpenAI API key in your environment variables or in the script
2. Use the detailed character description template or create your own
3. Customize output parameters as needed
4. Run the script to generate high-quality tailored images

Requirements:
- Python 3.6+
- openai library (pip install openai)
- Pillow library (pip install Pillow)
"""

import base64
import os
import time
import random
import json
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

def get_character_template():
    """Return a template for detailed character generation"""
    return """
    Character Specification

    Name: {name}
    
    Visual Appearance:
    - Body Shape: {body_shape}
    - Material/Texture: {texture}
    - Color Palette: {colors}
    - Facial Features: {facial_features}
    - Clothing/Accessories: {clothing}
    
    Environment/Background:
    - Setting: {setting}
    - Lighting: {lighting}
    - Mood: {mood}
    
    Style Reference:
    - Art Style: {art_style}
    - Render Quality: {render_quality}
    """

def generate_detailed_image(
    client, 
    character_specs,
    output_path,
    size="1024x1024", 
    quality="high", 
    output_format="png",
    output_compression=90
):
    """
    Generate an image using GPT Image API with detailed character specifications
    
    Args:
        client: OpenAI client instance
        character_specs: Dictionary of character specifications
        output_path: Path to save the generated image
        size: Image dimensions as 'widthxheight'. Options: '1024x1024', '1024x1536', '1536x1024'
        quality: Image quality. Options: 'low', 'medium', 'high', 'auto'
        output_format: File format for the output image. Options: 'png', 'jpeg', 'webp'
        output_compression: Compression level for the output image (0-100, only for jpeg/webp)
    
    Returns:
        Path to the saved image
    """
    try:
        # Create a prompt from the character specs using the template
        template = get_character_template()
        prompt = template.format(**character_specs)
        
        print(f"Generating detailed character image with specifications:")
        print(json.dumps(character_specs, indent=2))
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
        
        # Open and save the image
        image = Image.open(BytesIO(image_bytes))
        
        # Determine dimensions for display preview (keeping aspect ratio)
        width, height = image.size
        ratio = min(500 / width, 500 / height)
        preview_size = (int(width * ratio), int(height * ratio))
        
        preview = image.resize(preview_size, Image.Resampling.LANCZOS)
        
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

def get_sample_character_specs():
    """Return a sample character specification for demonstration"""
    return {
        "name": "Glorptak (Glorp)",
        "body_shape": "Amorphous and gelatinous. Overall silhouette resembles a teardrop or melting marshmallow, shifting slightly over time.",
        "texture": "Semi-translucent, bio-luminescent goo with a jelly-like wobble. Surface occasionally ripples.",
        "colors": "Base: Iridescent lavender or seafoam green. Accents: Neon pink, electric blue, golden yellow veins.",
        "facial_features": "3-5 asymmetrical floating orbs inside the blob that rotate or blink independently. Rippling crescent mouth when speaking.",
        "clothing": "None by default, but can extrude pseudopods (tentacle-like limbs) when needed for interaction.",
        "setting": "Futuristic laboratory with glowing equipment and mysterious substances.",
        "lighting": "Cool blue ambient light with warm accent lights highlighting key features.",
        "mood": "Curious and slightly mischievous, but friendly.",
        "art_style": "Digital 3D rendering with realistic lighting and textures.",
        "render_quality": "High-definition with attention to translucency and reflective surfaces."
    }

def get_random_character_specs():
    """Generate random character specifications for creative experimentation"""
    
    body_shapes = [
        "Tall and slender with elongated limbs", 
        "Short and stocky with powerful build",
        "Ethereal and wispy, partially transparent",
        "Mechanical with visible gears and components",
        "Amorphous and constantly shifting",
        "Crystalline with faceted surfaces"
    ]
    
    textures = [
        "Rough stone-like skin with moss patches",
        "Smooth metallic surface with a polished finish",
        "Scaly with iridescent reflections",
        "Fuzzy with short, soft fur",
        "Liquid-like with rippling surface",
        "Wooden with visible grain patterns"
    ]
    
    color_schemes = [
        "Deep blues and purples with silver highlights",
        "Earth tones - browns, greens, and warm ochres",
        "Fiery reds and oranges with yellow accents",
        "Monochromatic grayscale with one accent color",
        "Pastel rainbow palette with soft transitions",
        "Black and white with one vibrant color accent"
    ]
    
    settings = [
        "Ancient ruins overgrown with luminescent plants",
        "Futuristic cityscape with floating structures",
        "Underwater kingdom with bubble architecture",
        "Volcanic landscape with rivers of glowing magma",
        "Celestial realm among clouds and floating islands",
        "Dense forest with giant mushrooms and bioluminescent life"
    ]
    
    art_styles = [
        "Watercolor with soft edges and color bleeds",
        "Digital concept art with detailed rendering",
        "Comic book style with bold outlines",
        "Pixel art with limited color palette",
        "Photorealistic 3D rendering",
        "Claymation-inspired stylized look"
    ]
    
    # Generate a random character name
    syllables = ["zor", "gax", "plex", "tron", "nyx", "vex", "lum", "zar", "mek", "qua"]
    name = ''.join(random.sample(syllables, 2)).capitalize()
    
    return {
        "name": name,
        "body_shape": random.choice(body_shapes),
        "texture": random.choice(textures),
        "colors": random.choice(color_schemes),
        "facial_features": "Unique eyes that glow with inner light, expressive features that shift with mood",
        "clothing": "Outfit that reflects the character's environment and nature",
        "setting": random.choice(settings),
        "lighting": "Dramatic lighting that enhances the mood and highlights key features",
        "mood": random.choice(["mysterious", "heroic", "contemplative", "joyful", "melancholic"]),
        "art_style": random.choice(art_styles),
        "render_quality": "High-definition with attention to detail and atmosphere"
    }

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate detailed character images using OpenAI GPT Image API')
    parser.add_argument('--random', action='store_true', help='Generate random character specifications')
    parser.add_argument('--sample', action='store_true', help='Use sample character (Glorptak)')
    parser.add_argument('--size', type=str, default="1024x1024", choices=["1024x1024", "1024x1536", "1536x1024"],
                        help='Image dimensions (widthxheight)')
    parser.add_argument('--quality', type=str, default="high", choices=["low", "medium", "high", "auto"],
                        help='Image quality')
    parser.add_argument('--format', type=str, default="png", choices=["png", "jpeg", "webp"],
                        help='Output image format')
    args = parser.parse_args()
    
    # Setup
    client = setup_client()
    output_folder = create_output_folder()
    
    # Determine which character specs to use
    if args.sample:
        character_specs = get_sample_character_specs()
    elif args.random:
        character_specs = get_random_character_specs()
    else:
        # Default to sample if neither flag is specified
        character_specs = get_sample_character_specs()
    
    # Create a filename based on character name and timestamp
    timestamp = int(time.time())
    filename = f"{character_specs['name'].lower().replace(' ', '_')}_{timestamp}.{args.format}"
    output_path = os.path.join(output_folder, filename)
    
    # Generate the image
    generate_detailed_image(
        client, 
        character_specs,
        output_path,
        size=args.size, 
        quality=args.quality, 
        output_format=args.format
    )

if __name__ == "__main__":
    main()
