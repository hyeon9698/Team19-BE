import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

def generate_tts(text, speaker='vmikyung', volume=0, speed=-1, pitch=0, emotion=2, format='mp3', file_name='output.mp3'):
    client_id = "rip7iolwxf"
    client_secret = os.getenv("generate_tts")
    encText = urllib.parse.quote(text)
    data = f"speaker={speaker}&volume={volume}&speed={speed}&pitch={pitch}&format={format}&emotion={emotion}&text={encText}"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        with open(file_name, 'wb') as f:
            f.write(response_body)
    else:
        print("Error Code:", rescode)
    return file_name

if __name__ == '__main__':
    # text = "이거 말고 피자 먹고 싶어요."
    # generate_tts(text, file_name='give_me_pizza.mp3')
    text = "아니야 음식 먹고 싶어."
    generate_tts(text, file_name='no_again_explain2.mp3')

