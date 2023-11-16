import Bilingual
import json
import subprocess
from moviepy.editor import *
import handle_audio




def video2audio(video_name):
    my_audio_clip = AudioFileClip(video_name)
    my_audio_clip.write_audiofile('overview.wav')


def audio2srt():
    handle_audio.main()

    

def video_merge_srt(input_mp4):
    output_mp4 = "output.mp4"
    subtitles_srt = 'subtitle.srt'
    command = [
        "ffmpeg",
        "-i",
        input_mp4,
        "-vf",
        f"subtitles={subtitles_srt}:force_style='MarginV=60'",
        output_mp4,
    ]

    subprocess.run(command, check=True)

def video_merge_audio(video_name,audio_name):
    
    # 加载视频和音频文件
    video = VideoFileClip(video_name)
    audio = AudioFileClip(audio_name)

    # 将音频文件添加到视频文件中
    video = video.set_audio(audio)

    # 输出合并后的视频文件
    video.write_videofile("finally.mp4")


def main():
    video_name = 'overview.mp4'
    video2audio(video_name)
    audio2srt()
    video_merge_audio(video_name,'./audios/0.wav')
    video_merge_srt('finally.mp4')


if __name__ == '__main__':
    main()
