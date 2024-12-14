from downloading import download_video, download_audio
from transcription import select_file, process_transcription

import tkinter as tk
from tkinter import ttk


def create_gui():
    root = tk.Tk()
    root.title("Media Manager")

    notebook = ttk.Notebook(root)
    notebook.pack(padx=10, pady=10, fill='both', expand=True)

    # Tab 1: Video/Audio Download
    tab_download = ttk.Frame(notebook)
    notebook.add(tab_download, text="Download")

    frame_download = tk.Frame(tab_download)
    frame_download.pack(padx=10, pady=10)

    tk.Label(frame_download, text="Enter media URL:").pack()
    url_entry = tk.Entry(frame_download, width=50)
    url_entry.pack()

    download_video_button = tk.Button(
        frame_download,
        text="Download Video",
        command=lambda: handle_download(download_video, url_entry.get(), status_label)
    )
    download_video_button.pack(pady=5)

    download_audio_button = tk.Button(
        frame_download,
        text="Download Audio Only",
        command=lambda: handle_download(download_audio, url_entry.get(), status_label)
    )
    download_audio_button.pack(pady=5)

    status_label = tk.Label(frame_download, text="", fg="blue")
    status_label.pack()

    # Tab 2: Media Processing
    tab_process = ttk.Frame(notebook)
    notebook.add(tab_process, text="Process Media")

    frame_process = tk.Frame(tab_process)
    frame_process.pack(padx=10, pady=10)

    tk.Label(frame_process, text="Select a media file for processing:").pack()
    select_file_button = tk.Button(
        frame_process,
        text="Select File",
        command=lambda: select_file(process_status_label)
    )
    select_file_button.pack(pady=5)

    process_button = tk.Button(
        frame_process,
        text="Create Translation",
        command=lambda: process_transcription(process_status_label)
    )
    process_button.pack(pady=10)

    process_status_label = tk.Label(frame_process, text="", fg="blue")
    process_status_label.pack()

    root.mainloop()


def handle_download(download_function, url, status_label):
    if not url.strip():
        status_label.config(text="Please enter a URL!", fg="red")
        return

    try:
        download_function(url, status_label)
    except Exception as e:
        status_label.config(text="Download error. Check the URL.", fg="red")
        print(f"Error: {e}")


if __name__ == "__main__":
    create_gui()
