from pytube import YouTube
import os
from faster_whisper import WhisperModel
import asyncio
import edge_tts
from pydub import AudioSegment

def download_video(video_link):
    yt = YouTube(video_link)
    print('download...')
    yt.streams.filter().get_highest_resolution().download(filename='overview.mp4')
    print('ok!')

# download_video('https://www.youtube.com/watch?v=2KQUAKl6IaI')

