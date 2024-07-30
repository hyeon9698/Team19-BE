from openai import OpenAI
import os
import io
import base64
import requests
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class ChatGPTClass:
    def __init__(self, folder="data_00"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.folder = folder
        self.filename = ""
        self.question_index = -1
        self.response_data_history = ""
        # self.data = []
        # self.add_message("system", "당신은 사진을 보고 설명을 해주는 AI 입니다. 당신은 아이의 호기심을 해결해주는 친절한 부모입니다. 아이와 대화할 때는 아이의 궁금증을 해결해주고, 꼬리질문을 던지며 흥미를 지속시킵니다. 예시를 통해 설명하며, 답변은 짧고 명확하게 제공합니다. 대화는 항상 존대말로 해야합니다. 대화는 항상 질문으로 끝나야 합니다.")
        # self.question_index = 2 # 0: 아이가 처음 물어본 것, 1: 첫 사진을 보고 AI가 대답한 것, 2부터는 추가 질문에 대한 답변

    def add_message_with_image(self, image_input):
        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Function to encode the PIL type image
        def encode_pil_image(pil_image):
            buffered = io.BytesIO()
            pil_image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Check if input is a file path or PIL Image
        if isinstance(image_input, str):
            base64_image = encode_image(image_input)
        elif isinstance(image_input, Image.Image):
            base64_image = encode_pil_image(image_input)
        else:
            raise ValueError("Input must be either a file path (string) or a PIL Image object")

        self.data.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })

    def add_message(self, role, content):
        self.data.append({
            "role": role,
            "content": content
        })
        self.update_log({"role": role, "content": content})

    def remove_image_message(self):
        self.data.pop(1)

    def init_messages(self):
        self.data = []
        self.add_message("system", "당신은 사진을 보고 설명을 해주는 AI 입니다. 당신은 아이의 호기심을 해결해주는 친절한 부모입니다. 아이와 대화할 때는 아이의 궁금증을 해결해주고, 꼬리질문을 던지며 흥미를 지속시킵니다. 예시를 통해 설명하며, 답변은 짧고 명확하게 제공합니다. 아이가 지루해질 수 있기 때문에 2줄이 넘어가면 안됩니다. 대화는 항상 존대말로 해야합니다. 대화는 항상 질문으로 끝나야 합니다.")
        # self.question_index = 1 # 0: 아이가 처음 물어본 것, 1: 첫 사진을 보고 AI가 대답한 것, 2부터는 추가 질문에 대한 답변

    def update_log(self, message):
        self.question_index += 1
        with open(os.path.join("data", self.folder, "log.txt"), "a+", encoding="utf-8") as f:
            f.write(f"{self.question_index:02d}_{message['role']}: {message['content']}\n")

    def get_response(self):
        payload = {
            "model": "gpt-4o-mini",
            "messages": self.data
        }
        response = requests.post(self.url, headers=self.headers, json=payload)
        if response.status_code == 200:
            response_data = response.json()['choices'][0]['message']['content']
            self.add_message("assistant", response_data)
            self.response_data_history = response_data
            return response_data
        else:
            return "Error: " + response.text

if __name__ == '__main__':
    chatgpt = ChatGPTClass()
    chatgpt.add_message_with_image("./example_data/test.jpg")
    print(chatgpt.get_response())
    chatgpt.remove_image_message()
    breakpoint()
    chatgpt.add_message("user", "네 좋아해요 더 추천해주세요")
    chatgpt.add_message("user", "저는 치킨 좋아해요")
    chatgpt.add_message("user", "매콤한 거요")
    
    # list remove [1]