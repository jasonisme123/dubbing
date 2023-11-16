import json
import re
import time
from googletranslatepy import Translator
translator = Translator(proxies='http://127.0.0.1:7890')
def translate(sentence):
    while True:
        try:
            text = translator.translate(sentence)
            break
        except Exception as e:
            print(e)
            time.sleep(3)  # 等待 2 秒后重试
    return text

