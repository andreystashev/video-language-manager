from downloading import process_video_download, process_audio_download
from transcription import transcribe_audio, split_sentences, get_unique_words, select_file, process_transcription, \
    get_unique_words_with_dict
import threading


import tkinter as tk
from tkinter import ttk









# Основная функция для создания GUI
def create_gui():
    # Создаем главное окно
    root = tk.Tk()
    root.title("Видео загрузчик")

    # Создаем объект Notebook для вкладок
    notebook = ttk.Notebook(root)
    notebook.pack(padx=10, pady=10, fill='both', expand=True)

    # Вкладка 1: Загрузка видео/аудио
    tab_download = ttk.Frame(notebook)
    notebook.add(tab_download, text="Скачать")

    frame_download = tk.Frame(tab_download)
    frame_download.pack(padx=10, pady=10)

    tk.Label(frame_download, text="Ссылка на видео:").pack()
    url_entry = tk.Entry(frame_download, width=40)
    url_entry.pack()

    # Кнопка для скачивания видео
    download_video_button = tk.Button(frame_download, text="Скачать видео",
                                      command=lambda: process_video_download(url_entry.get(),
                                                                             status_label))
    download_video_button.pack(pady=5)

    # Кнопка для скачивания только аудио
    download_audio_button = tk.Button(frame_download, text="Скачать только аудио", command=lambda: process_audio_download(url_entry.get(),
                                                                             status_label))
    download_audio_button.pack(pady=5)

    # Метка для статуса
    status_label = tk.Label(frame_download, text="")
    status_label.pack()

    # Вкладка 2: Обработка файла
    tab_process = ttk.Frame(notebook)
    notebook.add(tab_process, text="Обработка")

    frame_process = tk.Frame(tab_process)
    frame_process.pack(padx=10, pady=10)

    tk.Label(frame_process, text="Выберите файл для обработки:").pack()
    select_file_button = tk.Button(frame_process, text="Выбрать файл", command=lambda: select_file(process_label))
    select_file_button.pack(pady=5)

    process_button = tk.Button(frame_process, text="Транскрибировать", command=lambda: process_transcription(process_label))
    process_button.pack(pady=10)

    process_label = tk.Label(frame_process, text="")
    process_label.pack()

    # Вкладка 3: Создание списка
    tab_process = ttk.Frame(notebook)
    notebook.add(tab_process, text="Создание списка")

    frame_list = tk.Frame(tab_process)
    frame_list.pack(padx=10, pady=10)

    tk.Label(frame_list, text="Выберите файл для обработки:").pack()
    select_file_button = tk.Button(frame_list, text="Выбрать файл", command=lambda: select_file(process_label))
    select_file_button.pack(pady=5)

    process_button = tk.Button(frame_list, text="Создать список", command=lambda: get_unique_words(process_label))
    process_button.pack(pady=10)

    process_button = tk.Button(frame_list, text="Создать проверенный список", command=lambda: get_unique_words_with_dict(process_label))
    process_button.pack(pady=10)


    process_button = tk.Button(frame_list, text="Перевести список", command=lambda: get_unique_words(process_label))
    process_button.pack(pady=10)

    process_label = tk.Label(frame_list, text="")
    process_label.pack()






    # Запуск главного цикла приложения
    root.mainloop()


if __name__ == "__main__":
    create_gui()

#https://www.youtube.com/watch?v=uTocTDcE0PY mgs codec