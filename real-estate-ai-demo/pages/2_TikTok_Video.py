import streamlit as st
import os
import dotenv
import requests
import base64
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import math
import google.generativeai as genai
import tempfile
from moviepy.editor import ImageClip, AudioFileClip
from moviepy.video.fx import speedx

dotenv.load_dotenv()

# Fetch the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('TikTok Video Generator')

# Function to get an image from a URL
def get_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Function to download images concurrently
def download_images_concurrently(image_urls):
    with ThreadPoolExecutor(max_workers=20) as executor:  # Adjust the number of workers as needed
        images = list(executor.map(get_image, image_urls))
    return images

# Function to create a grid of images
@st.cache_data
def create_image_grid(image_urls, grid_max_width=4):
    images = download_images_concurrently(image_urls)  # This will download all images concurrently

    if not images:
        raise ValueError("No images to display")

    # Assuming all images are the same size, get dimensions of the first image
    img_width, img_height = images[0].size
    
    # Calculate grid size
    num_images = len(images)
    grid_width = min(grid_max_width if grid_max_width else num_images, num_images)
    grid_height = math.ceil(num_images / grid_width)

    # Create a new image with a white background
    total_width = img_width * grid_width
    total_height = img_height * grid_height
    grid_image = Image.new('RGB', (total_width, total_height), 'white')

    # Paste images into the grid
    for index, image in enumerate(images):
        row = index // grid_width
        col = index % grid_width
        grid_image.paste(image, (col * img_width, row * img_height))

    return grid_image

# Function to encode the image to base64
def encode_image(image):
    # Convert the PIL Image to bytes
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    # Encode the bytes in base64
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

@st.cache_data
def generate_tiktok_video(generated_post, audio_data, image_urls, address):
    # Save the audio data to a file
    audio_buffer = BytesIO(audio_data)
    audio_buffer.seek(0)
    audio_file_path = 'generated_audio.mp3'
    with open(audio_file_path, 'wb') as audio_file:
        audio_file.write(audio_buffer.read())

    # Load the audio file and speed it up by 1.3 times
    audio_clip = AudioFileClip(audio_file_path)
    audio_clip = speedx(audio_clip, factor=1.0)  # Apply speedx with a factor of 1.3

    audio_duration = audio_clip.duration

address = st.text_input('Address', '126 Glenrose Ave')
community_name = st.text_input('Community Name', 'Rosedale-Moore Park')
municipality_name = st.text_input('Municipality Name', 'Toronto')
house_type = st.text_input('House Type', 'Detached')
property_desciption = st.text_area('Property description', '''LOCATION, LOCATION, LOCATION! Classic 2 1/2 Storey Detached Brick Home Loved By The Same Family For 54 Years. Featuring 4 Bedrooms Plus Den & Third Floor Loft Space! Extra Long 143' Deep Lot. Solid Double Brick Construction W/ Original Charm & Character W/ Oak Trim, Wainscotting & Hardwood Floors. Spacious Principal Rooms & Great Layout ( See Floorplans).Incredible Potential, Bring Your Designer/Contractor. Blank Canvas To Renovate Or Add On (12m Building Height Allowed). Superior School Catchment - Whitney Jr PS(10/10 Frasier Institute) Ranked #1 Public School In Ontario. Our Lady Of Perpetual Help(Catholic)(9.2). Branksome Hall, UCC, Greenwood ( Private Schools). Short Walk To Yonge & St Clair ,Trendy Shops/Restaurants & The TTC/Subway . Quick 10 Minute Drive To Downtown! Enjoy Strolls In Beautiful Moore Park Ravine/Beltline Trail, All Within Walking Distance. Steps Away From Moorevale Park/Tennis Club. A Beautiful Tree Lined Street In The Heart Of Rosedale-Moore Park!

Updated Windows, Updated Boiler System. Built In Bookcases. Large Garage (Completed With Permits). Separate Entrance To Basement. Fantastic Storage. ''')
photo_list_urls = st.text_area('Listing image url (1 per line)',
                               'https://cache08.housesigma.com/file/pix-treb/C8035418/1a783_1.jpg?73491889\nhttps://cache09.housesigma.com/file/pix-treb/C8035418/1a783_2.jpg?73491889\nhttps://cache18.housesigma.com/file/pix-treb/C8035418/1a783_5.jpg?73491889\nhttps://cache19.housesigma.com/file/pix-treb/C8035418/1a783_6.jpg?73491889\nhttps://cache-e11.housesigma.com/file/pix-treb/C8035418/1a783_7.jpg?73491889\nhttps://cache-e12.housesigma.com/file/pix-treb/C8035418/1a783_8.jpg?73491889\nhttps://cache-e13.housesigma.com/file/pix-treb/C8035418/1a783_9.jpg?73491889\nhttps://cache-e14.housesigma.com/file/pix-treb/C8035418/1a783_10.jpg?73491889\nhttps://cache05.housesigma.com/file/pix-treb/C8035418/1a783_11.jpg?73491889\nhttps://cache06.housesigma.com/file/pix-treb/C8035418/1a783_12.jpg?73491889\nhttps://cache16.housesigma.com/file/pix-treb/C8035418/1a783_15.jpg?73491889\nhttps://cache17.housesigma.com/file/pix-treb/C8035418/1a783_16.jpg?73491889\nhttps://cache-e12.housesigma.com/file/pix-treb/C8035418/1a783_20.jpg?73491889\nhttps://cache-e13.housesigma.com/file/pix-treb/C8035418/1a783_21.jpg?73491889\nhttps://cache-e14.housesigma.com/file/pix-treb/C8035418/1a783_22.jpg?73491889\nhttps://cache08.housesigma.com/file/pix-treb/C8035418/1a783_25.jpg?73491889')
image_urls = photo_list_urls.split('\n')

if property_desciption and address and image_urls:
    # Create a single grid image from the photo list
    grid_image = create_image_grid(image_urls)
    st.image(grid_image, caption='Generated Image Grid', use_column_width=True)
    # Encode the grid image to base64
    base64_image = encode_image(grid_image)

    # Save the grid image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        grid_image.save(temp_file, format="JPEG")
        temp_file_path = temp_file.name

    # Upload the image to Gemini Vision Pro
    sample_file = genai.upload_file(path=temp_file_path, display_name="grid_image.jpg")
    file = genai.get_file(name=sample_file.name)

    # Choose a Gemini API model
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    # Prepare the prompt
    prompt = f'''You are a realtor and social media marketing expert. Write a highly engaging & super short TikTok audio script (less than 30 seconds). Do NOT include notes about the video. A realtor will speak exactly what you write with a slideshow of the listing as the video. Do not include information about the video itself. Never include short-form words or acronyms like "sq ft", instead write "square feet" because the realtor will read exactly what you write. Do not state anything that may be untrue. No emojis. Keep it very short and engaging. Use the photos and information to the best of your ability. I have attached the photos, listing description and some other pieces of info about the property that you might find helpful. 
    house-address_navigation:   {address}
    house-community_name:  {community_name}
    house-municipality_name: {municipality_name}   
    house-house_type: {house_type}               
    Listing description: {property_desciption}
    '''

    if st.button('Generate TikTok Video'):
        # Prompt the model with text and the previously uploaded image
        response = model.generate_content([file, prompt])

        # Display the generated TikTok script
        st.subheader("Generated TikTok Script:")
        st.write(response.text)
else:
    st.error('Please enter a valid address.')