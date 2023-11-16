import json
from pydub import AudioSegment
from moviepy.editor import *
from datetime import timedelta
from faster_whisper import WhisperModel
import edge_tts
import asyncio
# from mutagen.mp3 import MP3
import re
import os
import Bilingual

last_end_time  = None
first_start_time_inSecond = None

def text_insert_srt(text, start_time, end_time, index):
    global first_start_time_inSecond
    output_file = 'subtitle.srt'
    with open(output_file, 'a', encoding='utf-8') as output:
        output.write(str(index) + '\n')
        if index == 1:
            model_size = "small"
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            segments, _ = model.transcribe("overview.wav", word_timestamps=True)
            for segment in segments:
                for word in segment.words:
                    first_start_time_inSecond = word.start
                    start_time = first_start_time_inSecond
                    break
                break
        start = adjust_time(start_time)
        end = adjust_time(end_time)
        output.write(f"{start} --> {end}\n")
        # output.write(text+'\n')
        translate_text = Bilingual.translate(text)
        output.write(translate_text)
        output.write('\n\n')
    return translate_text
        


def adjust_time(time_str):
    # 将字符串转换为浮点数
    time_in_seconds = float(time_str)

    # 将浮点数转换为时间差对象
    delta = timedelta(seconds=time_in_seconds)

    # 计算出小时、分钟、秒和毫秒
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = delta.microseconds // 1000

    # 将时间格式化为"00:02:12,560"的格式
    result = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    return result


def transcribe(audio_name):
    global first_start_time_inSecond
    model_size = "small"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_name, beam_size=5)

    for i, segment in enumerate(segments):
        segment_start = "{:.3f}".format(segment.start)
        segment_end = "{:.3f}".format(segment.end)
        segment_text = segment.text.strip()
        translate_text = text_insert_srt(segment_text, segment_start, segment_end, i+1)
        text_2_audio(translate_text,segment_start,segment_end,i)
      
    
    prefix_slient_time = first_start_time_inSecond*1000
    before_mp3 = get_mp3_duration('./audios/0.wav')
    ori_mp3 = get_mp3_duration('./overview.wav')
    after_mp3 = (ori_mp3 - before_mp3)*1000 - prefix_slient_time
    
    merge_end_silence(prefix_slient_time,after_mp3)


def text_2_audio(text,start_time,end_time,index,rate='+20%'):
    global last_end_time
    global first_start_time_inSecond
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tts = edge_tts.Communicate(text=text, voice="zh-CN-YunxiaNeural", rate=rate)
    audio_filePath = './audios/'+str(index)+'.mp3'
    loop.run_until_complete(tts.save(audio_filePath))
    loop.close()
    audio_duration = get_mp3_duration(audio_filePath)
    if (audio_duration > (float(end_time)-float(start_time))) and (rate!='+100%') :
        delete_audio_file(audio_filePath)
        try:
            get_rate = speed_audio(rate)
            text_2_audio(text,start_time,end_time,index,get_rate)
        except Exception as e:
            print(e)
    else:
        convert_mp3_to_wav(audio_filePath,'./audios/'+str(index)+'.wav')
        delete_audio_file(audio_filePath)
        audio_filePath = './audios/'+str(index)+'.wav'
        if index != 0:
            audio_gap = ((float(end_time)-float(start_time)) - audio_duration)*1000
            silence_gap = (float(start_time) - float(last_end_time))*1000
            if audio_gap < 0:
                if (silence_gap + audio_gap) < 0:
                    merge_mp3_with_silence(audio_filePath,0,0)
                else:
                    merge_mp3_with_silence(audio_filePath,silence_gap + audio_gap,0)
            else:
                merge_mp3_with_silence(audio_filePath,silence_gap,audio_gap)
            
            last_end_time = end_time
        else:
            prefix_slient_time = first_start_time_inSecond
            last_end_time = prefix_slient_time+get_mp3_duration(audio_filePath)

def convert_mp3_to_wav(mp3_file, wav_file):
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format='wav')



def merge_end_silence(start_silence_duration,end_silence_duration):
    audio1 = AudioSegment.from_wav('./audios/0.wav')
    # 创建静音段
    start_silence_segment = AudioSegment.silent(duration=int(start_silence_duration))
    end_silence_segment = AudioSegment.silent(duration=int(end_silence_duration))
    # 合并音频文件
    merged_audio = start_silence_segment + audio1 + end_silence_segment
    # 导出合并后的音频文件
    merged_audio.export('./audios/0.wav', format="wav")
    


def merge_mp3_with_silence(mp3_file, gap_silence_duration,remain_silence_duration):
    # 加载第一个MP3文件
    audio1 = AudioSegment.from_wav('./audios/0.wav')

    # 加载第二个MP3文件
    audio2 = AudioSegment.from_wav(mp3_file)

    # 创建静音段
    gap_silence_segment = AudioSegment.silent(duration=int(gap_silence_duration))
    remain_silence_segment = AudioSegment.silent(duration=int(remain_silence_duration))

    # 合并音频文件
    merged_audio = audio1 + gap_silence_segment + audio2 + remain_silence_segment

    # 导出合并后的音频文件
    merged_audio.export('./audios/0.wav', format="wav")
    
    delete_audio_file(mp3_file)
           

def speed_audio(input_rate):
    number_match = re.search(r'\d+', input_rate)
    if number_match:
        number = int(number_match.group())
        new_number = number + 5
        output_rate = re.sub(r'\d+', str(new_number), input_rate)
        return output_rate
    else:
        raise Exception("速率格式错误")
        
    
def delete_audio_file(file_path):
    try:
        os.remove(file_path)
        # print(f"音频文件 {file_path} 已成功删除")
    except OSError as e:
        print(f"删除音频文件 {file_path} 时发生错误: {e}")


def get_mp3_duration(file_path):
    sound = AudioSegment.from_mp3(file_path)
    duration_in_seconds = len(sound) / 1000
    return duration_in_seconds



def main():
    transcribe('overview.wav')


# main()
