import whisper
import re
from tkinter import filedialog
import ffmpeg
import os
import spacy
from nltk.corpus import words
from nltk.data import find
try:
    find('corpora/words.zip')
except LookupError:
    import nltk
    nltk.download('words')



def select_file(process_label):
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")])
    if file_path:
        process_label.config(text=f"Выбран файл: {file_path}")
        global selected_file_path
        selected_file_path = file_path


def process_transcription(process_label):
    if not selected_file_path:
        process_label.config(text="Сначала выберите файл!")
        return
    output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("txt files", "*.txt")])
    if not output_path:
        process_label.config(text="Transcription canceled")
        return
    if os.path.exists(output_path):
        os.remove(output_path)
    process_label.config(text="Обработка...")
    transcript = ""
    if selected_file_path.endswith('.mp3'):
        transcript = transcribe_audio(selected_file_path)
    elif selected_file_path.endswith('.mp4'):
        audio_path = 'extracted_audio.mp3'
        extract_audio(selected_file_path, audio_path)
        transcript = transcribe_audio(audio_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
    sentences = split_sentences(transcript)
    with open(output_path, "w", encoding="utf-8") as f:
        for sentence in sentences:
            print(sentence)
            f.write(sentence+"\n")
    process_label.config(text="Транскрипция завершена!")


def extract_audio(video_path, audio_path):
    ffmpeg.input(video_path).output(audio_path).run()


def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]


def split_sentences(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = []
    last_sentence = ""
    for sent in doc.sents:
        sentence = sent.text.strip()
        if sentence:
            words = sentence.split()
            filtered_words = []
            prev_word = None
            for word in words:
                if word != prev_word:
                    filtered_words.append(word)
                prev_word = word
            filtered_sentence = " ".join(filtered_words)
            if filtered_sentence == last_sentence:
                continue
            sentences.append(filtered_sentence)
            last_sentence = filtered_sentence
    return sentences



def get_unique_words(process_label):
    if not selected_file_path:
        process_label.config(text="Сначала выберите файл!")
        return
    output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("txt files", "*.txt")])
    if not output_path:
        process_label.config(text="Transcription canceled")
        return
    if os.path.exists(output_path):
        os.remove(output_path)
    process_label.config(text="Обработка...")
    with open(selected_file_path, "r", encoding="utf-8") as f:  # Читаем файл с форматированной транскрипцией
        transcript = f.read()
    # Извлекаем слова, приводим к нижнему регистру
    words = re.findall(r'\b\w+\b', transcript.lower())

    # Фильтруем слова:
    # 1. Убираем слова из одной буквы
    # 2. Убираем слова с цифрами
    # 3. Убираем слова с неанглийскими символами
    filtered_words = [
        word for word in words
        if len(word) > 1 and  # Слова длиной больше 1
           not any(char.isdigit() for char in word) and  # Без цифр
           re.fullmatch(r'[a-z]+', word)  # Только английские буквы
    ]

    unique_words = sorted(set(filtered_words))  # Убираем дубли и сортируем слова

    with open(output_path, "w", encoding="utf-8") as f:  # Сохраняем уникальные слова в новый файл
        f.write("\n".join(unique_words))  # Сохраняем каждое слово с новой строки

    print(f"Список уникальных слов сохранен в файл: {output_path}")


def get_unique_words_with_dict(process_label):
    if not selected_file_path:
        process_label.config(text="Сначала выберите файл!")
        return
    output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("txt files", "*.txt")])
    if not output_path:
        process_label.config(text="Transcription canceled")
        return
    if os.path.exists(output_path):
        os.remove(output_path)
    process_label.config(text="Обработка...")

    with open(selected_file_path, "r", encoding="utf-8") as f:  # Читаем файл с форматированной транскрипцией
        transcript = f.read()

    # Получаем список английских слов из NLTK
    english_words = set(words.words())

    # Извлекаем слова, приводим к нижнему регистру
    words_in_transcript = re.findall(r'\b\w+\b', transcript.lower())

    # Фильтруем слова:
    filtered_words = [
        word for word in words_in_transcript
        if len(word) > 1 and  # Слова длиной больше 1
           not any(char.isdigit() for char in word) and  # Без цифр
           re.fullmatch(r'[a-z]+', word) and  # Только английские буквы
           word in english_words  # Проверка, что слово существует в английском словаре
    ]

    unique_words = sorted(set(filtered_words))  # Убираем дубли и сортируем слова

    with open(output_path, "w", encoding="utf-8") as f:  # Сохраняем уникальные слова в новый файл
        f.write("\n".join(unique_words))  # Сохраняем каждое слово с новой строки

    process_label.config(text=f"Список уникальных слов сохранен в файл: {output_path}")
    print(f"Список уникальных слов сохранен в файл: {output_path}")