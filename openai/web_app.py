#!/usr/bin/env python3
"""
AI Image Generation Web Application

This script creates a simple web application for generating images using OpenAI's
GPT Image API. It provides a user-friendly interface for creating, editing, and 
downloading AI-generated images.

Features:
- Web-based user interface for image generation
- Support for editing existing images
- Mask generation and editing options
- Image download and sharing capabilities
- History of generated images

Usage:
1. Set your OpenAI API key in environment variables
2. Run the script to start the web application
3. Access the application through your web browser
4. Generate and edit images through the UI

Requirements:
- Python 3.6+
- Flask (pip install flask)
- openai library (pip install openai)
- Pillow library (pip install Pillow)
"""

import base64
import os
import time
import json
from io import BytesIO
from flask import Flask, request, render_template, jsonify, send_file
from PIL import Image
from openai import OpenAI

app = Flask(__name__)

# Configuration
IMAGE_FOLDER = "static/images"
MASK_FOLDER = "static/masks"
MAX_HISTORY = 20  # Number of images to keep in history

# Create necessary folders
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(MASK_FOLDER, exist_ok=True)

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OpenAI API key not found in environment variables!")
    print("Please set OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

# Session storage for image history
image_history = []

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html', history=image_history)

@app.route('/generate', methods=['POST'])
def generate_image():
    """Generate a new image using OpenAI GPT Image API"""
    try:
        # Get parameters from request
        data = request.json
        prompt = data.get('prompt', '')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        output_format = data.get('format', 'png')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate timestamp and filenames
        timestamp = int(time.time())
        filename = f"generated_{timestamp}.{output_format}"
        filepath = os.path.join(IMAGE_FOLDER, filename)
        
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
        
        # Save the image
        image = Image.open(BytesIO(image_bytes))
        image.save(filepath)
        
        # Add to history
        image_info = {
            'id': timestamp,
            'filename': filename,
            'prompt': prompt,
            'filepath': filepath,
            'created_at': timestamp,
            'type': 'generated'
        }
        
        image_history.append(image_info)
        if len(image_history) > MAX_HISTORY:
            image_history.pop(0)
        
        return jsonify({
            'success': True,
            'image': {
                'url': f"/static/images/{filename}",
                'id': timestamp,
                'prompt': prompt
            }
        })
    
    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/edit', methods=['POST'])
def edit_image():
    """Edit an existing image using OpenAI GPT Image API"""
    try:
        # Get parameters from request
        data = request.json
        image_id = data.get('image_id')
        prompt = data.get('prompt', '')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        use_mask = data.get('use_mask', False)
        
        if not image_id or not prompt:
            return jsonify({'error': 'Image ID and prompt are required'}), 400
        
        # Find the image in history
        image_info = next((img for img in image_history if img['id'] == image_id), None)
        if not image_info:
            return jsonify({'error': 'Image not found'}), 404
        
        # Generate timestamp and filenames
        timestamp = int(time.time())
        output_format = image_info['filename'].split('.')[-1]
        filename = f"edited_{timestamp}.{output_format}"
        filepath = os.path.join(IMAGE_FOLDER, filename)
        
        # Prepare the input image
        with open(image_info['filepath'], 'rb') as f:
            input_image = f.read()
        
        # Prepare mask if needed
        mask = None
        if use_mask and 'mask_filepath' in image_info:
            with open(image_info['mask_filepath'], 'rb') as f:
                mask = f.read()
        
        # Call OpenAI API to edit the image
        if mask:
            result = client.images.edit(
                model="gpt-image-1",
                image=input_image,
                mask=mask,
                prompt=prompt,
                size=size,
                quality=quality
            )
        else:
            result = client.images.edit(
                model="gpt-image-1",
                image=input_image,
                prompt=prompt,
                size=size,
                quality=quality
            )
        
        # Extract and decode the image data
        image_data = result.data[0].b64_json
        image_bytes = base64.b64decode(image_data)
        
        # Save the image
        image = Image.open(BytesIO(image_bytes))
        image.save(filepath)
        
        # Add to history
        edit_info = {
            'id': timestamp,
            'filename': filename,
            'prompt': prompt,
            'filepath': filepath,
            'original_id': image_id,
            'created_at': timestamp,
            'type': 'edited'
        }
        
        if mask:
            edit_info['mask_filepath'] = image_info['mask_filepath']
        
        image_history.append(edit_info)
        if len(image_history) > MAX_HISTORY:
            image_history.pop(0)
        
        return jsonify({
            'success': True,
            'image': {
                'url': f"/static/images/{filename}",
                'id': timestamp,
                'prompt': prompt
            }
        })
    
    except Exception as e:
        print(f"Error editing image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate-mask', methods=['POST'])
def generate_mask():
    """Generate a mask for an image using OpenAI GPT Image API"""
    try:
        # Get parameters from request
        data = request.json
        image_id = data.get('image_id')
        mask_prompt = data.get('mask_prompt', 'Generate a mask delimiting the main subject in the picture, using white for the subject and black for the background.')
        
        if not image_id:
            return jsonify({'error': 'Image ID is required'}), 400
        
        # Find the image in history
        image_info = next((img for img in image_history if img['id'] == image_id), None)
        if not image_info:
            return jsonify({'error': 'Image not found'}), 404
        
        # Generate timestamp and filenames
        timestamp = int(time.time())
        mask_filename = f"mask_{timestamp}.png"
        mask_filepath = os.path.join(MASK_FOLDER, mask_filename)
        
        # Prepare the input image
        with open(image_info['filepath'], 'rb') as f:
            input_image = f.read()
        
        # Call OpenAI API to generate the mask
        result = client.images.edit(
            model="gpt-image-1",
            image=input_image,
            prompt=mask_prompt
        )
        
        # Extract and decode the mask data
        mask_data = result.data[0].b64_json
        mask_bytes = base64.b64decode(mask_data)
        
        # Save the mask
        mask = Image.open(BytesIO(mask_bytes))
        mask.save(mask_filepath)
        
        # Convert to alpha mask
        alpha_mask_filename = f"mask_alpha_{timestamp}.png"
        alpha_mask_filepath = os.path.join(MASK_FOLDER, alpha_mask_filename)
        
        # Convert grayscale mask to RGBA with alpha channel
        mask_gray = mask.convert("L")
        mask_rgba = mask_gray.convert("RGBA")
        mask_rgba.putalpha(mask_gray)
        mask_rgba.save(alpha_mask_filepath)
        
        # Update the image info with mask path
        image_info['mask_filepath'] = alpha_mask_filepath
        
        return jsonify({
            'success': True,
            'mask': {
                'url': f"/static/masks/{alpha_mask_filename}",
                'id': timestamp
            }
        })
    
    except Exception as e:
        print(f"Error generating mask: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get the history of generated and edited images"""
    return jsonify({'history': image_history})

@app.route('/download/<int:image_id>', methods=['GET'])
def download_image(image_id):
    """Download an image by ID"""
    try:
        # Find the image in history
        image_info = next((img for img in image_history if img['id'] == image_id), None)
        if not image_info:
            return jsonify({'error': 'Image not found'}), 404
        
        return send_file(image_info['filepath'], as_attachment=True)
    
    except Exception as e:
        print(f"Error downloading image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete an image by ID"""
    try:
        # Find the image in history
        image_info = next((img for img in image_history if img['id'] == image_id), None)
        if not image_info:
            return jsonify({'error': 'Image not found'}), 404
        
        # Remove the file
        if os.path.exists(image_info['filepath']):
            os.remove(image_info['filepath'])
        
        # Remove from history
        image_history.remove(image_info)
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error deleting image: {e}")
        return jsonify({'error': str(e)}), 500

# HTML templates and static files would be placed in the appropriate folders:
# - templates/index.html: Main application UI
# - static/css/styles.css: CSS styling
# - static/js/app.js: JavaScript for UI interaction

if __name__ == '__main__':
    # Generate a basic HTML template if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    index_html_path = os.path.join(templates_dir, 'index.html')
    if not os.path.exists(index_html_path):
        with open(index_html_path, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Image Generator</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body>
    <div class="container">
        <h1>AI Image Generator</h1>
        
        <div class="generate-section">
            <h2>Generate New Image</h2>
            <textarea id="prompt" placeholder="Describe the image you want to generate..."></textarea>
            
            <div class="options">
                <select id="size">
                    <option value="1024x1024">Square (1024x1024)</option>
                    <option value="1024x1536">Portrait (1024x1536)</option>
                    <option value="1536x1024">Landscape (1536x1024)</option>
                </select>
                
                <select id="quality">
                    <option value="standard">Standard Quality</option>
                    <option value="medium">Medium Quality</option>
                    <option value="high">High Quality</option>
                </select>
                
                <select id="format">
                    <option value="png">PNG</option>
                    <option value="jpeg">JPEG</option>
                    <option value="webp">WebP</option>
                </select>
            </div>
            
            <button id="generate-btn">Generate Image</button>
        </div>
        
        <div class="result-section" style="display: none;">
            <h2>Generated Image</h2>
            <div class="image-container">
                <img id="result-image" src="" alt="Generated image">
            </div>
            
            <div class="image-actions">
                <button id="edit-btn">Edit Image</button>
                <button id="mask-btn">Generate Mask</button>
                <button id="download-btn">Download</button>
            </div>
            
            <div class="edit-section" style="display: none;">
                <textarea id="edit-prompt" placeholder="Describe how to edit the image..."></textarea>
                <div class="mask-option">
                    <input type="checkbox" id="use-mask">
                    <label for="use-mask">Use mask</label>
                </div>
                <button id="apply-edit-btn">Apply Edit</button>
            </div>
        </div>
        
        <div class="history-section">
            <h2>Image History</h2>
            <div class="history-container">
                {% for image in history %}
                <div class="history-item">
                    <img src="/static/images/{{ image.filename }}" alt="{{ image.prompt }}">
                    <div class="history-item-info">
                        <p>{{ image.prompt }}</p>
                        <button class="history-load-btn" data-id="{{ image.id }}">Load</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
            """)
    
    # Create basic CSS
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    css_dir = os.path.join(static_dir, 'css')
    os.makedirs(css_dir, exist_ok=True)
    
    css_path = os.path.join(css_dir, 'styles.css')
    if not os.path.exists(css_path):
        with open(css_path, 'w') as f:
            f.write("""
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1, h2 {
    color: #333;
}

textarea {
    width: 100%;
    min-height: 100px;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: Arial, sans-serif;
}

.options {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 15px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 4px;
}

.image-container {
    margin: 20px 0;
    text-align: center;
}

.image-container img {
    max-width: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.image-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-bottom: 20px;
}

.history-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.history-item {
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.history-item img {
    width: 100%;
    height: 150px;
    object-fit: cover;
}

.history-item-info {
    padding: 10px;
}

.history-item-info p {
    margin: 0 0 10px 0;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.history-load-btn {
    font-size: 14px;
    padding: 5px 10px;
}
            """)
    
    # Create basic JavaScript
    js_dir = os.path.join(static_dir, 'js')
    os.makedirs(js_dir, exist_ok=True)
    
    js_path = os.path.join(js_dir, 'app.js')
    if not os.path.exists(js_path):
        with open(js_path, 'w') as f:
            f.write("""
// DOM Elements
const promptInput = document.getElementById('prompt');
const sizeSelect = document.getElementById('size');
const qualitySelect = document.getElementById('quality');
const formatSelect = document.getElementById('format');
const generateBtn = document.getElementById('generate-btn');
const resultSection = document.querySelector('.result-section');
const resultImage = document.getElementById('result-image');
const editBtn = document.getElementById('edit-btn');
const maskBtn = document.getElementById('mask-btn');
const downloadBtn = document.getElementById('download-btn');
const editSection = document.querySelector('.edit-section');
const editPromptInput = document.getElementById('edit-prompt');
const useMaskCheckbox = document.getElementById('use-mask');
const applyEditBtn = document.getElementById('apply-edit-btn');
const historyLoadBtns = document.querySelectorAll('.history-load-btn');

// Current state
let currentImageId = null;
let hasMask = false;

// Event listeners
generateBtn.addEventListener('click', generateImage);
editBtn.addEventListener('click', () => {
    editSection.style.display = 'block';
});
maskBtn.addEventListener('click', generateMask);
downloadBtn.addEventListener('click', downloadImage);
applyEditBtn.addEventListener('click', editImage);

// Add event listeners to history load buttons
historyLoadBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const imageId = parseInt(btn.getAttribute('data-id'));
        loadImageFromHistory(imageId);
    });
});

// Functions
async function generateImage() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }
    
    try {
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                size: sizeSelect.value,
                quality: qualitySelect.value,
                format: formatSelect.value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultImage.src = data.image.url + '?t=' + new Date().getTime(); // Add timestamp to prevent caching
            currentImageId = data.image.id;
            hasMask = false;
            resultSection.style.display = 'block';
            editSection.style.display = 'none';
            useMaskCheckbox.checked = false;
            useMaskCheckbox.disabled = true;
            
            // Refresh the page to update history
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            alert(data.error || 'Error generating image');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating image');
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Image';
    }
}

async function editImage() {
    if (!currentImageId) {
        alert('No image selected');
        return;
    }
    
    const prompt = editPromptInput.value.trim();
    if (!prompt) {
        alert('Please enter an edit prompt');
        return;
    }
    
    try {
        applyEditBtn.disabled = true;
        applyEditBtn.textContent = 'Applying...';
        
        const response = await fetch('/edit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_id: currentImageId,
                prompt: prompt,
                size: sizeSelect.value,
                quality: qualitySelect.value,
                use_mask: useMaskCheckbox.checked && hasMask
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultImage.src = data.image.url + '?t=' + new Date().getTime(); // Add timestamp to prevent caching
            currentImageId = data.image.id;
            editSection.style.display = 'none';
            
            // Refresh the page to update history
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            alert(data.error || 'Error editing image');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error editing image');
    } finally {
        applyEditBtn.disabled = false;
        applyEditBtn.textContent = 'Apply Edit';
    }
}

async function generateMask() {
    if (!currentImageId) {
        alert('No image selected');
        return;
    }
    
    try {
        maskBtn.disabled = true;
        maskBtn.textContent = 'Generating Mask...';
        
        const response = await fetch('/generate-mask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_id: currentImageId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hasMask = true;
            useMaskCheckbox.disabled = false;
            useMaskCheckbox.checked = true;
            alert('Mask generated successfully');
        } else {
            alert(data.error || 'Error generating mask');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating mask');
    } finally {
        maskBtn.disabled = false;
        maskBtn.textContent = 'Generate Mask';
    }
}

function downloadImage() {
    if (!currentImageId) {
        alert('No image selected');
        return;
    }
    
    window.location.href = `/download/${currentImageId}`;
}

function loadImageFromHistory(imageId) {
    // Fetch image details
    fetch(`/history`)
        .then(response => response.json())
        .then(data => {
            const image = data.history.find(img => img.id === imageId);
            if (image) {
                resultImage.src = `/static/images/${image.filename}?t=${new Date().getTime()}`;
                currentImageId = image.id;
                hasMask = 'mask_filepath' in image;
                resultSection.style.display = 'block';
                editSection.style.display = 'none';
                useMaskCheckbox.disabled = !hasMask;
                useMaskCheckbox.checked = hasMask;
                
                // Scroll to the result section
                resultSection.scrollIntoView({ behavior: 'smooth' });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error loading image');
        });
}
            """)
    
    print(f"Starting AI Image Generator app on http://127.0.0.1:5000")
    app.run(debug=True)
