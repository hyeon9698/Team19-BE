import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from PIL import Image
import traceback
# from utils.gpt_image_analyze import analyze_image
from utils.clova_stt import stt_function
from utils.clova_tts import generate_tts
from utils.chatgpt_class import ChatGPTClass
from utils.utils import check_folder, get_directory_structure, telegram_send_message, plot_big_tag, telegram_send_image
import shutil
from utils.gpt_image_generateion import generate_image
from fastapi.staticfiles import StaticFiles
import datetime
import json
from collections import Counter

app = FastAPI()

app.mount("/data", StaticFiles(directory="data"), name="data")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "https://team19-fe.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
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

@app.get("/init_model/{kids_age}")
async def init_model(kids_age: str):
    global GPT_CLASS, FOLDER
    print("kids_age", kids_age)
    FOLDER = check_folder()
    GPT_CLASS = ChatGPTClass(folder=FOLDER, kids_age=kids_age)

@app.post("/analyze_image_and_return_response_and_audio")
async def analyze_image_and_return_response_and_audio(file: UploadFile = File(...)):
    try:
        print("사진 분석중 ...")
        # FOLDER = check_folder()
        # GPT_CLASS = ChatGPTClass(folder=FOLDER)
        os.makedirs(os.path.join("data", FOLDER), exist_ok=True)
        image = Image.open(file.file)
        image.save(os.path.join("data", FOLDER, "test.jpg"))
        GPT_CLASS.filename = "test.jpg".split(".")[0]
        GPT_CLASS.init_messages()
        GPT_CLASS.add_message_with_image(image)
        response_data = GPT_CLASS.get_response()
        GPT_CLASS.remove_index_message(1)
        GPT_CLASS.add_message("user", "이전 대화를 참고해서, 아이가 좋아할 제목으로 사용할 만큼 짧게 작성해줘. 예를 들어서 사진에 사자가 들어가 있다면: 무시무시한 사자!", update_log=False)
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
        # print(GPT_CLASS.question_index+1)
        response_data = GPT_CLASS.response_data_history
        if GPT_CLASS.kids_age == "2":
            output_mp3_path = generate_tts(response_data, file_name=os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index:02d}.mp3"))
        elif GPT_CLASS.kids_age == "1":
            output_mp3_path = generate_tts(response_data, file_name=os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index:02d}.mp3"), speed=0)
        elif GPT_CLASS.kids_age == "0":
            output_mp3_path = generate_tts(response_data, file_name=os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index:02d}.mp3"), speed=1)
        return FileResponse(output_mp3_path, media_type="audio/mpeg")
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/get_generated_image_data")
async def get_generated_image_data():
    try:
        print("GPT_CLASS.question_index", GPT_CLASS.question_index)
        # if GPT_CLASS.question_index == 5:
        if GPT_CLASS.question_index == 11:
            print("이미지 생성중 ...")
            generated_image = generate_image(str(GPT_CLASS.data))
            generated_image_path = os.path.join("data", FOLDER, f"generated_image.jpg")
            generated_image.save(generated_image_path)
            # return FileResponse(generated_image_path, media_type="image/jpeg")
            # return {"status": "success", "generated_image_path": generated_image_path}
            return JSONResponse({"status": "success", "generated_image_path": '/'+generated_image_path.replace("\\", "/")})
        else:
            print("이미지 생성 안함")
            return JSONResponse({"status": "success", "generated_image_path": "nono"})
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
        if GPT_CLASS.kids_age == "2" and GPT_CLASS.question_index >= 6:
            # 질문 그만하도록 prompt 변경
            print("질문 그만하도록 prompt 변경")
            audio_text_add = "[sytem message: 지금까지 한 대화를 활용해 질문을 이제 그만할 수 있도록 넛지를 넣어주세요. 예를 들어서: 부모님이 이 질문은 잘 답할거야!]"
            audio_text_added = audio_text + audio_text_add
            GPT_CLASS.add_message("user", audio_text_added, update_log=False)
            response_data_dict = {"role": "user", "content": audio_text}
            GPT_CLASS.update_log(message=response_data_dict)
        elif GPT_CLASS.kids_age == "1" and GPT_CLASS.question_index >= 6:
            # 질문 그만하도록 prompt 변경
            print("질문 그만하도록 prompt 변경")
            audio_text_add = "[sytem message: 지금까지 한 대화를 활용해 질문을 이제 그만할 수 있도록 넛지를 넣어주세요. 예를 들어서: 부모님이 이 질문은 잘 답할거야!]"
            audio_text_added = audio_text + audio_text_add
            GPT_CLASS.add_message("user", audio_text_added, update_log=False)
            response_data_dict = {"role": "user", "content": audio_text}
            GPT_CLASS.update_log(message=response_data_dict)
        elif GPT_CLASS.kids_age == "0" and GPT_CLASS.question_index >= 4:
            # 질문 그만하도록 prompt 변경
            print("질문 그만하도록 prompt 변경")
            audio_text_add = "[sytem message: 지금까지 한 대화를 활용해 질문을 이제 그만할 수 있도록 넛지를 넣어주세요. 예를 들어서: 부모님이 이 질문은 잘 답할거야!]"
            audio_text_added = audio_text + audio_text_add
            GPT_CLASS.add_message("user", audio_text_added, update_log=False)
            response_data_dict = {"role": "user", "content": audio_text}
            GPT_CLASS.update_log(message=response_data_dict)
        else:
            GPT_CLASS.add_message("user", audio_text)
        response_data = GPT_CLASS.get_response()
        print("AI 대답:", response_data)
        return {"status": "success", "user_input_data": audio_text, "response_data": response_data, "question_index": GPT_CLASS.question_index}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/voice_test_test")
async def voice_test_test(file: UploadFile = File(...)):
    try:
        print("voice_test_test 들어옴")
        audio_file_path = os.path.join("data", FOLDER, f"{GPT_CLASS.filename}_voice_{GPT_CLASS.question_index+1:02d}.mp3")
        with open(audio_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return FileResponse(audio_file_path, media_type="audio/mpeg")
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.get("/finish_messages")
async def finish_messages():
    try:
        GPT_CLASS.add_message("user", "지금까지 한 대화를 짧게 알려줘. 질문은 안해도 돼. ~가 뭐야? 형식으로 작성해줘. 예를 들어서 사자 내용이 들어가 있다면: 사자가 뭐야?, 자전거가 들어가 있다면: 자전거가 뭐야?", update_log=False)
        response_data = GPT_CLASS.get_response(update_log=False)
        response_data_dict = {"role": "short_summary", "content": response_data}
        GPT_CLASS.update_log(message=response_data_dict)
        GPT_CLASS.add_message("user", "지금까지 한 대화를 요약해서 알려줘. 재미있게 요약해서 알려줘. 아이와 어떤 대화를 나눴는지 알려줘", update_log=False)
        response_data = GPT_CLASS.get_response(update_log=False)
        response_data_dict = {"role": "long_summary", "content": response_data}
        GPT_CLASS.update_log(message=response_data_dict)
        GPT_CLASS.add_message("user", "지금까지 AI와 아이가 주고 받은 대화를 바탕으로, 부모가 아이에게 할 수 있는 질문 1가지를 알려줘. 1번 질문은 쉽게 주고 받을 수 있는 질문으로 만들어줘", update_log=False)
        response_data = GPT_CLASS.get_response(update_log=False)
        response_data_dict_1 = {"role": "recommend_questions_1", "content": response_data}
        GPT_CLASS.add_message("user", "지금까지 AI와 아이가 주고 받은 대화를 바탕으로, 부모가 아이에게 할 수 있는 질문 1가지를 알려줘. 질문은 행동에 관한 질문이면 좋겠어. (음식 이야기를 했다면: 같이 음식을 만들어 볼까요?)", update_log=False)
        response_data_question_2 = GPT_CLASS.get_response(update_log=False)
        response_data_dict_2 = {"role": "recommend_questions_2", "content": response_data_question_2}
        GPT_CLASS.update_log(message=response_data_dict_1)
        GPT_CLASS.update_log(message=response_data_dict_2)

        # 동물 음식 장소 물건 캐릭터 놀이 탈것 자연 스포츠 모험
        big_tag_list = ["동물", "음식", "장소", "물건", "캐릭터", "놀이", "탈것", "자연", "스포츠", "모험"]
        GPT_CLASS.add_message("user", f"지금까지 AI와 아이가 주고 받은 대화를 바탕으로, 아이가 좋아할 만한 태그를 선택해줘. 최소 3개 최대 5개 해줘. 아래 중에서 선택해줘: {', '.join(big_tag_list)}. 출력 결과값에 해당 단어가 있으면 태그로 표현할거야.", update_log=False)
        response_data = GPT_CLASS.get_response(update_log=False)
        # response_data 안에 big_tag_list에 있는 단어가 있으면 태그로 표현
        big_tag_list_2 = []
        for tag in big_tag_list:
            if tag in response_data:
                big_tag_list_2.append(tag)
        response_data_dict_3 = {"role": "big_tag", "content": ', '.join(big_tag_list_2)}
        GPT_CLASS.update_log(message=response_data_dict_3)
        GPT_CLASS.add_message("user", f"지금까지 AI와 아이가 주고 받은 대화를 바탕으로, 아이가 키워드 태그를 선택해줘. 최대 5개 선택해줘. 답만 보여주고 태그는 콤마(,)로 구분할거야.", update_log=False)
        response_data = GPT_CLASS.get_response(update_log=False)
        small_tag_list = response_data.split(", ")
        response_data_dict_4 = {"role": "small_tag", "content": response_data}
        GPT_CLASS.update_log(message=response_data_dict_4)
        response_data_dict_5 = {"role": "date", "content": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        GPT_CLASS.update_log(message=response_data_dict_5)
        telegram_send_message(f"😀모야Q에서 오늘의 질문 도착!\nQ. {response_data_question_2}")
        try:
            data = await get_all_data()
            data = json.loads(data.body.decode())
            plot_big_tag(data)
            telegram_send_image("./data/plot.png")
        except:
            pass
        return {"status": "success"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error removing last message: {str(e)}")

@app.get("/my_data")
async def my_data():
    try:
        data = await get_all_data()
        data = json.loads(data.body.decode())
        # breakpoint()
        # all_big_tags = [tag for entry in data.values() for tag in entry["big_tag"]]
        all_big_tags = []
        for entry in data.values():
            if "big_tag" in entry:
                for tag in entry["big_tag"]:
                    all_big_tags.append(tag)
        # Count the occurrences of each big tag
        tag_counts = Counter(all_big_tags)
        # breakpoint()
        # Get the top 4 most common big tags
        top_tag = tag_counts.most_common(4)
        return_big_tag, count = zip(*top_tag)
        # all_small_tags = [tag for entry in data.values() for tag in entry["small_tag"]]
        all_small_tags = []
        for entry in data.values():
            if "small_tag" in entry:
                for tag in entry["small_tag"]:
                    all_small_tags.append(tag)
        # get one data.keys() that has the most common big tag
        recommend_question = "질문이 없어요!"
        for key, value in data.items():
            # breakpoint()
            if "big_tag" in value:
                if return_big_tag[0] in value["big_tag"]:
                    recommend_question = value["recommend_questions_1"]
        if len(all_small_tags) > 8:
            all_small_tags = all_small_tags[:8]
        return {"status": "success", "plot_data_path": "/data/plot.png", "tag": return_big_tag, "count": count, "all_small_tags": all_small_tags, "recommend_question": recommend_question}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting my data: {str(e)}")

@app.get("/get_all_data")
async def get_all_data():
    try:
        rootdir = './data'  # Set the root directory
        data_structure = get_directory_structure(rootdir)
        return JSONResponse(content=data_structure)
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting all data: {str(e)}")

@app.get("/get_one_data/{folder_name}")
async def get_one_data(folder_name: str):
    try:
        print("folder_name", folder_name)
        rootdir = './data'
        data_structure = get_directory_structure(rootdir)
        if folder_name in data_structure:
            return JSONResponse(content=data_structure[folder_name])
        else:
            raise HTTPException(status_code=404, detail="Folder not found")
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting one data: {str(e)}")

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