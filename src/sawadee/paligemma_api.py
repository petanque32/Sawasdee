import requests
from PIL import Image
from io import BytesIO
import base64
import json


# Define the API endpoint
def paligemma_call(image_path,prompt='caption thai'):
    url = 'https://5cee-1-20-14-86.ngrok-free.app/vqa/'

    # Define the parameters for the POST request
    params = {
        'prompt': prompt,
        'save_raw_image':'false',
    }
    files = {
        'image_bytes': ('menu1.jpeg', open(image_path, 'rb'), 'image/jpeg')
    }

    # Make the POST request to the API
    response = requests.post(url, params=params, files=files)

    return response.json()
