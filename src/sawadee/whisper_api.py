import requests
from PIL import Image
from io import BytesIO
import base64
import json


# Define the API endpoint
def whisper_call(wave_path,translate=False,api='cWGjkb1dJcyDIg8g6DYmW64g0ccGgLWp'):
    url = 'https://5cee-1-20-14-86.ngrok-free.app/asr/'
    
    # Define the parameters for the POST request
    params = {
    'translate': translate,  # or False, depending on your requirement
    'translate_to_speech': translate,  # or False
    'file_format': 'mp3',  # specify the file format you need
    'api_key_ai4thai': api
    }

    files = {
        'sound_bytes': ('audio_sample.mp3', open(wave_path, 'rb'), 'audio/mpeg')
    }

    # Make the POST request
    response = requests.post(url, params=params, files=files)



    return response.json()

