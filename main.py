import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from PIL import Image
from typing import List
import json
from utils.gpt_image_analyze import analyze_image
from utils.clova_stt import stt_function
from utils.clova_tts import generate_tts
import tempfile
from threading import Thread
from utils.chatgpt_class import ChatGPTClass
from utils.utils import play_sound

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if os.path.exists("data"):
    folders = os.listdir("data")
    if len(folders) > 0:
        folders.sort()
        last_folder = folders[-1]
        last_folder_number = int(last_folder.split("_")[-1])
        FOLDER = f"data_{last_folder_number+1:02d}"
    else:
        FOLDER = "data_00"
GPT_CLASS = ChatGPTClass(folder=FOLDER)

# @app.post("/get_image_info")
# async def get_image_info(file: UploadFile = File):
#     try:
#         # Get the file name
#         file_name = file.filename
#         # Open the image using PIL
#         image = Image.open(file.file)
#         # Get the image size
#         width, height = image.size
#         # Prepare the response
#         image_info = {
#             "file_name": file_name,
#             "width": width,
#             "height": height,
#             "format": image.format,
#             "mode": image.mode
#         }
#         return image_info
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# test
@app.get("/")
async def read_root():
    return {"Hello": "World"}

# image test
@app.post("/test_image")
async def test_image(file: UploadFile = File):
    # return image info
    try:
        print(file)
        # Get the file name
        file_name = file.filename
        # Open the image using PIL
        image = Image.open(file.file)
        # Get the image size
        width, height = image.size
        # Prepare the response
        image_info = {
            "file_name": file_name,
            "width": width,
            "height": height,
            "format": image.format,
            "mode": image.mode
        }
        return image_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# audio test
@app.get("/get_audio")
async def get_audio():
    try:
        return FileResponse("give_me_pizza.mp3", media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")







# audio test
@app.post("/test_audio")
async def test_audio(file: UploadFile = File):
    try:
        file_name = file.filename
        audio_info = {
            "file_name": file_name,
            "format": file.format,
            "mode": file.mode
        }
        return audio_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

# 이미지 파일을 업로드 받아서 이미지를 분석하고, 분석 결과를 mp3 파일로 저장하고, return은 분석 결과와 mp3 파일 경로를 반환합니다.
@app.post("/analyze_image_and_return_response_and_audio")
async def analyze_image_and_return_response_and_audio(file: UploadFile = File):
    try:
        print("analyze_image 진행중...")
        if not os.path.exists(os.path.join("data", FOLDER)):
            os.makedirs(os.path.join("data", FOLDER))
        image = Image.open(file.file)
        image.save(os.path.join("data", FOLDER, file.filename))
        GPT_CLASS.filename = file.filename.split(".")[0]
        GPT_CLASS.init_messages()
        GPT_CLASS.add_message_with_image(image)
        response_data = GPT_CLASS.get_response()
        GPT_CLASS.response_data_history = response_data
        return {"status": "success", "response_data": response_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/analyze_image_and_return_response_and_audio_2")
async def analyze_image_and_return_response_and_audio_2():
    try:
        response_data = GPT_CLASS.response_data_history
        GPT_CLASS.remove_image_message()
        output_mp3_path = generate_tts(response_data, file_name=os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_01.mp3"))
        return FileResponse(output_mp3_path, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# 아이가 추가로 질문한 내용을 받아서 답변을 생성하는 API. string 형태로 질문을 받아서 mp3 파일로 저장을 하고, string 형태로 답변을 반환합니다.
def get_response(question: str):
    try:
        GPT_CLASS.add_message("user", question)
        response_data = GPT_CLASS.get_response()
        output_mp3_path = generate_tts(response_data, file_name=os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index:02d}.mp3"))
        # GPT_CLASS.question_index += 1

        # T = Thread(target=play_sound, args=(output_mp3_path,))
        # T.start()
        return {"status": "success", "response_data": response_data, "output_mp3_path": output_mp3_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

# 유저의 목소리가 담긴 mp3 파일을 업로드 받아서 텍스트로 변환하는 API
@app.post("/analyze_voice_and_return_response_and_audio")
async def analyze_voice_and_return_response_and_audio(file: UploadFile = File):
    try:
        # 우선 file을 다운 받아서 저장
        audio_file_path = os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index+1:02d}.mp3")
        with open(audio_file_path, "wb") as f:
            f.write(file.file.read())

        # STT 함수를 호출하여 텍스트로 변환합니다.
        audio_text = stt_function(audio_file_path)['text']
        print("음성인식 결과:", audio_text)
        # 텍스트를 가지고 응답을 반환합니다.
        response_data = get_response(question=audio_text)
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

# 뒤로 가기 버튼을 눌렀을 때 초기화하는 API
@app.post("/init_messages")
async def init_messages():
    try:
        GPT_CLASS.init_messages()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing last message: {str(e)}")


# # 텍스트를 음성으로 변환하는 API
# @app.post("/get_audio_from_text")
# async def get_audio_from_text(text: str = Form(...)):
#     try:
#         # 텍스트를 음성으로 변환합니다.
#         generate_tts(text, file_name='output.mp3')
#         # 변환된 음성 파일을 반환합니다.
#         return {"status": "success"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

# 현재 GPT_CLASS 정보 반환
@app.get("/get_gpt_class_info")
async def get_gpt_class_info():
    try:
        return {"status": "success", "gpt_class_data": GPT_CLASS.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting gpt class info: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", reload=True)
    # 실행코드
    # conda activate santa
    # uvicorn main:app --port 8080
    # ngrok http 8080