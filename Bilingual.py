import pysrt
import json
import re
import time
from googletranslatepy import Translator
import baidu_translate_spider_api as baidu_translator
translator = Translator(proxies='http://127.0.0.1:7890')
def translate(sentence):
    while True:
        try:
            text = translator.translate(sentence)
            # text = baidu_translator.baidutrans(sentence)
            break
        except Exception as e:
            print(e)
            time.sleep(2)  # 等待 2 秒后重试
    return text

