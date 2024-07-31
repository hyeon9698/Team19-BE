from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import requests

load_dotenv()

def generate_image(input_conversation):
    client = OpenAI()
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Create a simple and cute animation-style illustration based on the following description from a conversation with a child: {input_conversation}. The illustration should be colorful and cheerful, with a soft and playful design. The characters and elements should have rounded features and a friendly appearance to appeal to children. Keep the overall composition balanced and engaging.",
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    # save image
    image = Image.open(requests.get(image_url, stream=True).raw)
    return image
