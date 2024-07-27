import streamlit as st
import openai
import os
import dotenv
import json
import requests
import base64
import json
import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import math
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # Get the original property listing description from the user

st.title('Facebook Post Generator')


# Function to get an image from a URL
@st.cache_data
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
# Function to encode the image
# Function to encode the image to base64
def encode_image(image):
    # Convert the PIL Image to bytes
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    # Encode the bytes in base64
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


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

    # Prepare the headers and payload for the OpenAI API call
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"  # Use Streamlit secrets to store API key securely
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f'''You are a realtor and social media marketing expert. Write a highly captivating Facebook post for the real estate listing. Do not state anything that may be untrue. Use the photos and information to the best of your ability. Use emojis. I have attached the photos, listing description and some other pieces of info about the property that you might find helpful. 
    house-address_navigation:   {address}
    house-community_name:  {community_name}
    house-municipality_name: {municipality_name}   
    house-house_type: {house_type}               
    Listing description: {property_desciption}
    '''
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }
    if st.button('Generate Facebook Post'):
        # Make the OpenAI API call
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Check if the response is successful
        if response.status_code == 200:
            # Extract the generated post from the response
            generated_post = response.json()['choices'][0]['message']['content']

            # Display the generated Facebook post
            st.subheader("Generated Facebook Post:")
            st.write(generated_post)
        else:
            st.error("Failed to generate post. Error: " + response.text)
