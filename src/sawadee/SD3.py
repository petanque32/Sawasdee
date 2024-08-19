import requests
from PIL import Image
from io import BytesIO
import base64



# Define the API endpoint
def sd3_call(prompt):
    # Define the API endpoint
    url = 'https://3788-49-228-212-148.ngrok-free.app/generate_image/'

    # Define the parameters for the POST request
    params = {
    'text': prompt,
    'negative_prompt': '',
    'num_inference_steps': 28,
    'guidance_scale': 7,
    'max_sequence_length': 512
    }
    
    # Make the POST request to the API
    response = requests.post(url, params=params)

    if response.status_code == 200:
        # Extract the base64 encoded image data from the response
        image_data = response.json().get('image_bytes')

        # Decode the base64 encoded image data
        image_bytes = base64.b64decode(image_data)

        # Convert the byte data to a PIL image
        image = Image.open(BytesIO(image_bytes))

        return image
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")

    return response.json()