import requests
import json

from dotenv import load_dotenv

load_dotenv()

def stt_function(file, completion='sync', callback=None, userdata=None, forbiddens=None, boostings=None,
                wordAlignment=True, fullText=True, diarization=None, sed=None):
    # Clova Speech invoke URL
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/8618/a97a2510bf9d982fbbeb48369f2caad4126bab55ee5c155435ae5d6d93cc7efe'
    # Clova Speech secret key
    secret = os.getenv("STT_FUNCTION")

    request_body = {
        'language': 'ko-KR',
        'completion': completion,
        'callback': callback,
        'userdata': userdata,
        'wordAlignment': wordAlignment,
        'fullText': fullText,
        'forbiddens': forbiddens,
        'boostings': boostings,
        'diarization': {'enable': False},
        'sed': sed,
    }
    headers = {
        'Accept': 'application/json;UTF-8',
        'X-CLOVASPEECH-API-KEY': secret
    }
    # print(json.dumps(request_body, ensure_ascii=False).encode('UTF-8'))
    files = {
        'media': open(file, 'rb'),
        'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
    }
    data = requests.post(headers=headers, url=invoke_url + '/recognizer/upload', files=files)
    data = json.loads(data.text)
    result = {
        "text": data.get("text"),
        "confidence": data.get("confidence"),
    }
    return result

if __name__ == '__main__':
    # res = ClovaSpeechClient().req_url(url='http://example.com/media.mp3', completion='sync')
    # res = ClovaSpeechClient().req_object_storage(data_key='data/media.mp3', completion='sync')
    res = ClovaSpeechClient().req_upload(file='./example_data/fast.mp3', completion='sync')
    print(res)