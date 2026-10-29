"""Create an English vocabulary list from local MP3 or MP4 media."""

from functools import lru_cache
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from tkinter import filedialog

import eng_to_ipa as ipa
from deep_translator import GoogleTranslator
from nltk.corpus import words
import whisper


selected_file_path = None


def select_file(process_label):
    file_path = filedialog.askopenfilename(
        filetypes=[("MP3 files", "*.mp3"), ("MP4 files", "*.mp4")]
    )
    if file_path:
        global selected_file_path
        selected_file_path = file_path
        process_label.config(text=f"Selected file: {file_path}")


def process_transcription(process_label):
    if not selected_file_path:
        process_label.config(text="Please select a file first!")
        return
    if Path(selected_file_path).suffix.lower() not in {".mp3", ".mp4"}:
        process_label.config(text="Please select an MP3 or MP4 file")
        return

    output_path = filedialog.asksaveasfilename(
        defaultextension=".txt", filetypes=[("Text files", "*.txt")]
    )
    if not output_path:
        process_label.config(text="Transcription canceled")
        return
    if Path(output_path).resolve() == Path(selected_file_path).resolve():
        process_label.config(text="Please choose an output file different from the source media")
        return

    temporary_path = None
    try:
        process_label.config(text="Generating transcription...")
        # Whisper uses FFmpeg and accepts video directly; no shared scratch file is needed.
        transcript = transcribe_audio(selected_file_path)
        process_label.config(text="Creating word list...")
        word_list = get_unique_words_from_text(transcript, use_dict=True)
        process_label.config(text="Translating words...")
        translated_list = process_translations(word_list)

        process_label.config(text="Saving file...")
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=Path(output_path).parent,
            prefix=".vocabulary-", suffix=".tmp", delete=False,
        ) as output:
            temporary_path = output.name
            output.writelines(translated_list)
        os.replace(temporary_path, output_path)
        temporary_path = None
        process_label.config(text=f"File successfully saved: {output_path}")
    except LookupError:
        process_label.config(text="Missing NLTK word corpus. Run: python -m nltk.downloader words")
    except Exception as error:
        process_label.config(text=f"Processing failed: {error}")
    finally:
        if temporary_path is not None:
            Path(temporary_path).unlink(missing_ok=True)


@lru_cache(maxsize=1)
def _load_model():
    return whisper.load_model("base")


def transcribe_audio(audio_path):
    return _load_model().transcribe(audio_path, language="en")["text"]


def get_unique_words_from_text(text, use_dict=False):
    english_words = set(words.words()) if use_dict else None
    words_in_text = re.findall(r"\b\w+\b", text.lower())
    return sorted({
        word for word in words_in_text
        if len(word) > 1 and re.fullmatch(r"[a-z]+", word)
        and (not use_dict or word in english_words)
    })


def process_translations(words_list):
    if not words_list:
        return []

    translator = GoogleTranslator(source="en", target="ru")
    translated_lines = []
    for word in words_list:
        if not word:
            continue
        translation = translator.translate(word) or ""
        transcription = ipa.convert(word)
        translated_lines.append(f"{word.ljust(33)}|{transcription.ljust(33)}|{translation}\n")
    return translated_lines
