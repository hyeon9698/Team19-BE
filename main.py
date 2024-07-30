import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from PIL import Image
import traceback
from utils.gpt_image_analyze import analyze_image
from utils.clova_stt import stt_function
from utils.clova_tts import generate_tts
from utils.chatgpt_class import ChatGPTClass
from utils.utils import check_folder
import shutil

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://team19-fe.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/voice_test")
async def voice_test(file: UploadFile = File(...)):
    try:
        print("file.filename", file.filename)
        audio_path = file.filename
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        audio_text = stt_function(audio_path)['text']
        print(audio_text)
        return {"audio_text": audio_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/test_image")
async def test_image(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file)
        image_info = {
            "file_name": file.filename,
            "width": image.size[0],
            "height": image.size[1],
            "format": image.format,
            "mode": image.mode
        }
        return image_info
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/test_audio")
async def test_audio(file: UploadFile = File(...)):
    try:
        audio_info = {
            "file_name": file.filename,
            "format": file.content_type,
        }
        return audio_info
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/analyze_image_and_return_response_and_audio")
async def analyze_image_and_return_response_and_audio(file: UploadFile = File(...)):
    global GPT_CLASS, FOLDER
    try:
        print("사진 분석중 ...")
        FOLDER = check_folder()
        GPT_CLASS = ChatGPTClass(folder=FOLDER)
        os.makedirs(os.path.join("data", FOLDER), exist_ok=True)
        image = Image.open(file.file)
        image.save(os.path.join("data", FOLDER, file.filename))
        GPT_CLASS.filename = file.filename.split(".")[0]
        GPT_CLASS.init_messages()
        GPT_CLASS.add_message_with_image(image)
        response_data = GPT_CLASS.get_response()
        GPT_CLASS.remove_index_message(1)
        GPT_CLASS.add_message("user", "아이가 좋아할 제목으로 사용할 만큼 짧게 작성해줘. 예를 들어서 사진에 사자가 들어가 있다면: '무시무시한 사자!'", update_log=False)
        response_data_summary = GPT_CLASS.get_response(update_log=False)
        GPT_CLASS.remove_index_message(2)
        print("요약된 문장:", response_data_summary)
        print("첫 번째 AI 대답:", response_data)
        return {"status": "success", "response_data": response_data, "response_data_summary": response_data_summary}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/get_audio_data")
async def get_audio_data():
    try:
        response_data = GPT_CLASS.response_data_history
        output_mp3_path = generate_tts(response_data, file_name=os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index:02d}.mp3"))
        return FileResponse(output_mp3_path, media_type="audio/mpeg")
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/analyze_voice_and_return_response_and_audio")
async def analyze_voice_and_return_response_and_audio(file: UploadFile = File(...)):
    try:
        audio_file_path = os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index+1:02d}.mp3")
        with open(audio_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        audio_text = stt_function(audio_file_path)['text']
        print("audio_text", audio_text)
        GPT_CLASS.add_message("user", audio_text)
        response_data = GPT_CLASS.get_response()
        return {"status": "success", "response_data": response_data}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.get("/finish_messages")
async def finish_messages():
    try:
        GPT_CLASS.add_message("user", "지금까지 한 대화를 한 문장으로 요약해서 알려줘. 질문은 안해도 돼. 아이와 대화하는 듯한 문장으로 만들어줘, 예를 들어서 사자 내용이 들어가 있다면: '무시무시한 사자가 나타났다!'", update_log=False)
        response_data = GPT_CLASS.get_response(update_log=False)
        response_data_dict = {"role": "summary", "content": response_data}
        GPT_CLASS.update_log(message=response_data_dict)
        return {"status": "success"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error removing last message: {str(e)}")

@app.get("/get_gpt_class_info")
async def get_gpt_class_info():
    try:
        return {"status": "success", "gpt_class_data": GPT_CLASS.data}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting gpt class info: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", reload=True)
    # conda activate team19
    # lt -p 8080 -s test
    # ngrok http 8080
    # uvicorn main:app --port 8080