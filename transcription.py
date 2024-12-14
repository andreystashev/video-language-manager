import whisper
import re
from tkinter import filedialog
import ffmpeg
import os
from nltk.corpus import words
from nltk.data import find

import eng_to_ipa as ipa
from deep_translator import GoogleTranslator

try:
    find('corpora/words.zip')
except LookupError:
    import nltk

    nltk.download('words')


def select_file(process_label):
    file_path = filedialog.askopenfilename(
        filetypes=[("MP3 files", "*.mp3"), ("MP4 files", "*.mp4"), ("All files", "*.*")])
    if file_path:
        process_label.config(text=f"Selected file: {file_path}")
        global selected_file_path
        selected_file_path = file_path


def process_transcription(process_label):
    if not selected_file_path:
        process_label.config(text="Please select a file first!")
        return

    output_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt"), ("Header files", "*.h"),
                                                          ("All files", "*.*")])
    if not output_path:
        process_label.config(text="Transcription canceled")
        return

    if os.path.exists(output_path):
        os.remove(output_path)

    process_label.config(text="Generating transcription...")
    transcript = ""
    if selected_file_path.endswith('.mp3'):
        transcript = transcribe_audio(selected_file_path)
    elif selected_file_path.endswith('.mp4'):
        audio_path = 'extracted_audio.mp3'
        ffmpeg.input(selected_file_path).output(audio_path).run()
        transcript = transcribe_audio(audio_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

    process_label.config(text="Creating word list...")
    word_list = get_unique_words_from_text(transcript, use_dict=True)

    process_label.config(text="Translating words...")
    translated_list = process_translations(word_list)

    process_label.config(text="Saving file...")
    with open(output_path, "w", encoding="utf-8") as f:
        for word in translated_list:
            f.write(word)

    process_label.config(text=f"File successfully saved: {output_path}")


def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]


def get_unique_words_from_text(text, use_dict=False):
    english_words = set(words.words()) if use_dict else None
    words_in_text = re.findall(r'\b\w+\b', text.lower())

    filtered_words = [
        word for word in words_in_text
        if len(word) > 1 and
           not any(char.isdigit() for char in word) and
           re.fullmatch(r'[a-z]+', word)
           and (not use_dict or word in english_words)
    ]

    unique_words = sorted(set(filtered_words))
    return unique_words


def process_translations(words_list):
    if not words_list:
        return

    translated_lines = []
    for word in words_list:
        if not word:
            continue
        translations = GoogleTranslator(source='auto', target="ru").translate(word)
        transcription = ipa.convert(word)

        if translations:
            formatted_line = (
                f"{word.ljust(33)}|{transcription.ljust(33)}|{translations}\n"
            )
        else:
            formatted_line = (
                f"{word.ljust(33)}|{transcription.ljust(33)}|{' '.ljust(33)}\n"
            )
        translated_lines.append(formatted_line)

    return translated_lines
