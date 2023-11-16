import json
import random
import time

import requests
from flask import Flask, request

# app = Flask(__name__)


def init_data(source_lang: str, target_lang: str):
    return {
        "jsonrpc": "2.0",
        "method": "LMT_handle_texts",
        "id": random.randint(100000, 109999) * 1000,
        "params": {
            "splitting": "newlines",
            "lang": {
                "source_lang_user_selected": source_lang,
                "target_lang": target_lang,
            },
        },
    }


def get_i_count(translate_text: str) -> int:
    return translate_text.count("i")


def get_random_number() -> int:
    return (random.randint(100000, 109999) * 1000)


def get_timestamp(i_count: int) -> int:
    ts = int(time.time() * 1000)
    if i_count != 0:
        i_count = i_count + 1
        return ts - ts % i_count + i_count
    else:
        return ts



def read_root():
    return {"code": 200, "msg": "Go to /translate with POST."}



def translate(data):
    try:
        translate_text = ''
        source_lang = 'AUTO'
        target_lang = 'AUTO'
        if 'text' in data:
            translate_text = data['text']
        if 'source_lang' in data:
            source_lang = data['source_lang']
        if 'target_lang' in data:
            target_lang = data['target_lang']
        if translate_text:
            url = "https://www2.deepl.com/jsonrpc"
            post_data = init_data(source_lang, target_lang)
            text = {
                "text": translate_text,
                "requestAlternatives": 3,
            }
            post_data["params"]["texts"] = [text]
            post_data["params"]["timestamp"] = get_timestamp(get_i_count(translate_text))
            post_str = json.dumps(post_data)
            if (post_data["id"] + 5) % 29 == 0 or (post_data["id"] + 3) % 13 == 0:
                post_str = post_str.replace('"method":"', '"method" : "', 1)
            else:
                post_str = post_str.replace('"method":"', '"method": "', 1)
            response = requests.post(url, post_str, headers={'Content-Type': 'application/json'})
            # print(response.text)

            response_json = json.loads(response.text)
            return response_json
    except Exception as e:
        raise e


if __name__ == '__main__':
    for i in range(0,15):
        while True:
            demodata = {
                'text':'i am good,what about you?',
                'source_lang':'en',
                'target_lang':'zh'
                }
            try:
                res = translate(demodata)
                print(res['result']['texts'][0]['alternatives'][0]['text'])
                break
            except Exception as e:
                print('休息一会')
                time.sleep(2)
            