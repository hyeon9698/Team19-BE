# from openai import OpenAI
# import os
# import io
# import base64
# import requests
# from PIL import Image
# from dotenv import load_dotenv

# load_dotenv()

# # def analyze_image(image_input, prompt="What's in this image?"):
# def analyze_image(image_input, prompt="당신은 사진을 보고 설명을 해주는 AI 입니다. 당신은 아이의 호기심을 해결해주는 친절한 부모입니다. 아이와 대화할 때는 아이의 궁금증을 해결해주고, 꼬리질문을 던지며 흥미를 지속시킵니다. 예시를 통해 설명하며, 답변은 짧고 명확하게 제공합니다. 대화는 항상 존대말로 해야합니다. 대화는 항상 질문으로 끝나야 합니다."):
#     # OpenAI API Key
#     api_key = os.getenv("generate_tts")

#     # Function to encode the image
#     def encode_image(image_path):
#         with open(image_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode('utf-8')

#     # Function to encode the PIL type image
#     def encode_pil_image(pil_image):
#         buffered = io.BytesIO()
#         pil_image.save(buffered, format="PNG")
#         return base64.b64encode(buffered.getvalue()).decode('utf-8')

#     # Check if input is a file path or PIL Image
#     if isinstance(image_input, str):
#         base64_image = encode_image(image_input)
#     elif isinstance(image_input, Image.Image):
#         base64_image = encode_pil_image(image_input)
#     else:
#         raise ValueError("Input must be either a file path (string) or a PIL Image object")

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }

#     payload = {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": prompt
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ],
#         "max_tokens": 300
#     }

#     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

#     return response.json()

# if __name__ == "__main__":
#     # Example usage
#     image_path = "path/to/your/image.jpg"
#     prompt = "Describe this image in detail."
#     result = analyze_image(image_path, prompt)
#     print(result)