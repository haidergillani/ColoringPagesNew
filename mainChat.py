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
import zipfile
import os

from dotenv import load_dotenv

load_dotenv()


# Set OpenAI API key using Streamlit Secrets
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize session state to store previously generated images
if 'images' not in st.session_state:
    st.session_state['images'] = []

# Streamlit app layout
st.title("Image Generator with DALLE")
st.write("Describe an image and get it generated in a coloring book style!")

# Textbox for user input
user_input = st.text_input("Enter a description for the image:")

# Button to generate image
if st.button("Generate Image"):
    if user_input:
        try:
            # Generate the image using DALLE
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

# Layout with sidebar for image buffer and action buttons
st.sidebar.title("Image Buffer")
st.sidebar.write("Previously generated images:")

# Scrollable area for previously generated images
if st.session_state['images']:
    for idx, image in enumerate(st.session_state['images']):
        st.sidebar.image(image, caption=f"Image {idx + 1}", use_column_width=True)
else:
    st.sidebar.write("No images generated yet.")

# Clear buffer button
if st.sidebar.button("Clear Buffer"):
    st.session_state['images'] = []

# Function to download all images as a zip file
def download_images():
    # Create a zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for idx, img in enumerate(st.session_state['images']):
            img_filename = f"image_{idx + 1}.png"
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            zf.writestr(img_filename, img_bytes.getvalue())
    zip_buffer.seek(0)  # Ensure buffer is at the beginning before downloading
    return zip_buffer

# Download button to download all images as a zip
if st.sidebar.button("Download All"):
    if st.session_state['images']:
        zip_file = download_images()
        st.sidebar.download_button(
            label="Download Images as ZIP",
            data=zip_file,
            file_name="generated_images.zip",
            mime="application/zip"
        )
    else:
        st.sidebar.write("No images to download.")

# Function to print images (opens images in a new tab or printable format)
def print_images():
    for img in st.session_state['images']:
        img.show()

# Print button
if st.sidebar.button("Print All"):
    if st.session_state['images']:
        print_images()
    else:
        st.sidebar.write("No images to print.")