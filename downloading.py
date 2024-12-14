import yt_dlp
import os
from tkinter import filedialog

def download_video(video_url, status_label):
    save_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])

    if not save_path:
        status_label.config(text="Download canceled: No file path selected")
        return

    if os.path.exists(save_path):
        os.remove(save_path)

    download_options = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': save_path,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(download_options) as ydl:
            ydl.download([video_url])
        status_label.config(text="Video successfully downloaded!")
    except yt_dlp.utils.DownloadError:
        status_label.config(text="Download error: Invalid video URL or network issue")
    except Exception as e:
        status_label.config(text=f"An unexpected error occurred: {e}")


def download_audio(audio_url, status_label):
    save_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])

    if not save_path:
        status_label.config(text="Download canceled: No file path selected")
        return

    if os.path.exists(save_path):
        os.remove(save_path)

    download_options = {
        'format': 'bestaudio/best',
        'outtmpl': save_path,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(download_options) as ydl:
            ydl.download([audio_url])
        status_label.config(text="Audio successfully downloaded!")
    except yt_dlp.utils.DownloadError:
        status_label.config(text="Download error: Invalid audio URL or network issue")
    except Exception as e:
        status_label.config(text=f"An unexpected error occurred: {e}")
