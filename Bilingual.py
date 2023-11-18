import json
import re
import time
from googletranslatepy import Translator
import deepl_translate
translator = Translator(proxies='http://127.0.0.1:7890')
def translate(sentence):
    while True:
        try:
            text = translator.translate(sentence)#Google翻译
            # text = deepl_translate.deepLtranslator(sentence) #deepL翻译
            break
        except Exception as e:
            print(e)
            time.sleep(3)  # 等待 2 秒后重试
    return text

