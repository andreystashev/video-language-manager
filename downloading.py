"""Download media to a temporary file before replacing the chosen destination."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from tkinter import filedialog

import yt_dlp


def _download_media(url, status_label, extension, options):
    save_path = filedialog.asksaveasfilename(
        defaultextension=f".{extension}",
        filetypes=[(f"{extension.upper()} files", f"*.{extension}")],
    )
    if not save_path:
        status_label.config(text="Download canceled: No file path selected")
        return

    try:
        destination = Path(save_path)
        # Keep temporary files beside the destination so replacement is atomic.
        with TemporaryDirectory(dir=destination.parent, prefix=".media-download-") as directory:
            download_options = {
                **options,
                "outtmpl": str(Path(directory) / "media.%(ext)s"),
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(download_options) as ydl:
                ydl.download([url.strip()])
            os.replace(Path(directory) / f"media.{extension}", destination)
        status_label.config(text="Media successfully downloaded!")
    except yt_dlp.utils.DownloadError:
        status_label.config(text="Download error: Check the URL, network, and FFmpeg installation")
    except Exception as error:
        status_label.config(text=f"Download failed: {error}")


def download_video(video_url, status_label):
    _download_media(video_url, status_label, "mp4", {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "postprocessors": [{"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}],
    })


def download_audio(audio_url, status_label):
    _download_media(audio_url, status_label, "mp3", {
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    })
