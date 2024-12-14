import yt_dlp
import os
from tkinter import filedialog



def process_video_download(url, status_label):
    output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])

    if not output_path:
        status_label.config(text="Download canceled")
        return

    if os.path.exists(output_path):
        os.remove(output_path)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        #print(f"Видео загружено: {output_path}")
        status_label.config(text="Video downloaded!")
    except Exception as error:
        #print(f"Ошибка при загрузке видео: {error}")
        status_label.config(text="Error video download")



def process_audio_download(url, status_label):
    output_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])

    if not output_path:
        status_label.config(text="Download canceled")
        return

    if os.path.exists(output_path):
        os.remove(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        #print(f"Аудио загружено: {output_path}")
        status_label.config(text="Audio downloaded!")
    except Exception as error:
        #print(f"Ошибка при загрузке аудио: {error}")
        status_label.config(text="Error audio download")


#https://www.youtube.com/watch?v=uTocTDcE0PY mgs codec
