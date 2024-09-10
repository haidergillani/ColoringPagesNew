# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 11:41:02 2024

@author: salacasa
"""
   
import streamlit as st
import openai
import requests
from PIL import Image
from io import BytesIO
import base64
import zipfile
import os

from dotenv import load_dotenv

load_dotenv()


# Set OpenAI API key using Streamlit Secrets
openai.api_key = os.getenv('OPENAI_API_KEY')

# Dummy images for testing
def load_fake_images():
    img1 = Image.new('RGB', (1024, 1024), color='red')
    img2 = Image.new('RGB', (1024, 1024), color='blue')
    st.session_state['images'] = [img1, img2]

# Initialize session state to store previously generated images
if 'images' not in st.session_state:
    load_fake_images()  # Load fake images at the start

# Streamlit app layout
st.title("Coloring Book Generator")
st.write("For testing purposes, two random images are preloaded.")

# Textbox for user input
user_input = st.text_input("Enter a description for your coloring page:")

# Button to generate an image using the new OpenAI API syntax
if st.button("Generate Image"):
    if user_input:
        try:
            # Generate the image using the new OpenAI API syntax
            response = openai.images.generate(
                model='dall-e-3',
                prompt=f"{user_input}, coloring book style",
                n=1,
                size="1024x1024"
            )
            
            # Extract the image URL from the response
            image_url = response.data[0].url
            
            # Fetch the image from the URL and display it
            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))

            # Add the image to the session state buffer
            st.session_state['images'].append(img)
            
            st.image(img, caption="Generated Image", use_column_width=True)
        except Exception as e:
            st.write(f"An error occurred: {e}")
    else:
        st.write("Please enter a description to generate an image.")

# Function to convert image to base64
def image_to_base64(image):
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
    return img_base64

# Function to generate HTML for printing the image with margins and centered
def generate_print_image_html(image_base64):
    return f"""
        <html>
        <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                width: 100vw;
                page-break-before: always;
            }}
            img {{
                max-width: 8.5in;
                max-height: 9in;  /* Reduced max height to leave space for top/bottom margins */
                margin-top: 1in;  /* Add top margin */
                margin-bottom: 1in;  /* Add bottom margin */
                display: block;
            }}
        </style>
        </head>
        <body onload="window.print(); window.onafterprint = window.close();">
            <img src="data:image/png;base64,{image_base64}" />
        </body>
        </html>
    """

# Function to generate HTML for printing all images
def generate_print_all_images_html(image_base64_list):
    image_tags = "\n".join(
        [f'<img src="data:image/png;base64,{img}" />' for img in image_base64_list]
    )
    
    return f"""
        <html>
        <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
            img {{
                max-width: 8.5in;
                max-height: 9in;
                margin-top: 1in;
                margin-bottom: 1in;
                display: block;
                page-break-before: always;
            }}
        </style>
        </head>
        <body onload="window.print(); window.onafterprint = window.close();">
            {image_tags}
        </body>
        </html>
    """

# Sidebar for image buffer and action buttons
st.sidebar.title("Image Buffer")
st.sidebar.write("Previously generated images:")

# Scrollable area for previously generated images
if st.session_state['images']:
    for idx, image in enumerate(st.session_state['images']):
        st.sidebar.image(image, caption=f"Image {idx + 1}", use_column_width=True)
        
        # Specific print button for each image
        if st.sidebar.button(f"Print Image {idx + 1}"):
            img_base64 = image_to_base64(image)
            print_html = generate_print_image_html(img_base64)
            st.components.v1.html(print_html, height=0)

        # Specific download button for each image
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        st.sidebar.download_button(
            label=f"Download Image {idx + 1}",
            data=img_bytes,
            file_name=f"image_{idx + 1}.png",
            mime="image/png"
        )
    
    # Print all images button
    if st.sidebar.button("Print All Images"):
        image_base64_list = [image_to_base64(img) for img in st.session_state['images']]
        print_all_html = generate_print_all_images_html(image_base64_list)
        st.components.v1.html(print_all_html, height=0)

else:
    st.sidebar.write("No images generated yet.")

# Clear buffer button
if st.sidebar.button("Clear Buffer"):
    st.session_state['images'] = []

# Function to create a zip file of all images
def download_images_zip():
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for idx, img in enumerate(st.session_state['images']):
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            zf.writestr(f"image_{idx + 1}.png", img_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# Download all images in a zip file
if st.sidebar.button("Download All as Zip"):
    zip_file = download_images_zip()
    st.sidebar.download_button(
        label="Download Images as ZIP",
        data=zip_file,
        file_name="images.zip",
        mime="application/zip"
    )
