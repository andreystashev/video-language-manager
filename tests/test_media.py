"""Regression checks with external services and model dependencies replaced by fakes."""

import importlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import types
import unittest
from unittest.mock import Mock, patch


def module(name, **attributes):
    fake = types.ModuleType(name)
    fake.__dict__.update(attributes)
    return fake


class DownloadError(Exception):
    pass


# Do not install a model, access a translation service, or download media in tests.
with patch.dict(sys.modules, {
    "yt_dlp": module("yt_dlp", YoutubeDL=Mock(), utils=types.SimpleNamespace(DownloadError=DownloadError)),
    "whisper": module("whisper", load_model=Mock()),
    "eng_to_ipa": module("eng_to_ipa", convert=Mock()),
    "deep_translator": module("deep_translator", GoogleTranslator=Mock()),
    "nltk": module("nltk"),
    "nltk.corpus": module("nltk.corpus", words=Mock()),
}):
    downloading = importlib.import_module("downloading")
    transcription = importlib.import_module("transcription")


class DownloadTests(unittest.TestCase):
    def test_audio_is_converted_to_mp3_and_replaces_file_after_success(self):
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "audio.mp3"
            destination.write_bytes(b"previous audio")
            label = Mock()

            def youtube_dl(options):
                self.assertEqual(options["postprocessors"][0]["preferredcodec"], "mp3")
                self.assertIn("%(ext)s", options["outtmpl"])
                fake = Mock()
                fake.__enter__ = Mock(return_value=fake)
                fake.__exit__ = Mock(return_value=False)

                def download(urls):
                    self.assertEqual(urls, ["https://example.com/media"])
                    self.assertEqual(destination.read_bytes(), b"previous audio")
                    Path(options["outtmpl"].replace("%(ext)s", "mp3")).write_bytes(b"converted mp3")

                fake.download.side_effect = download
                return fake

            with patch.object(downloading.filedialog, "asksaveasfilename", return_value=str(destination)), \
                    patch.object(downloading.yt_dlp, "YoutubeDL", side_effect=youtube_dl):
                downloading.download_audio(" https://example.com/media ", label)
            self.assertEqual(destination.read_bytes(), b"converted mp3")
            self.assertEqual(list(Path(directory).iterdir()), [destination])

    def test_failed_download_preserves_existing_destination(self):
        with TemporaryDirectory() as directory:
            destination = Path(directory) / "video.mp4"
            destination.write_bytes(b"keep me")
            label = Mock()
            with patch.object(downloading.filedialog, "asksaveasfilename", return_value=str(destination)), \
                    patch.object(downloading.yt_dlp, "YoutubeDL", side_effect=DownloadError("offline")):
                downloading.download_video("https://example.com/media", label)
            self.assertEqual(destination.read_bytes(), b"keep me")
            self.assertEqual(list(Path(directory).iterdir()), [destination])
            self.assertIn("Download error", label.config.call_args.kwargs["text"])

    def test_video_requests_mp4_container(self):
        with patch.object(downloading, "_download_media") as download:
            downloading.download_video("url", Mock())
        options = download.call_args.args[3]
        self.assertEqual(options["merge_output_format"], "mp4")
        self.assertEqual(options["postprocessors"][0], {
            "key": "FFmpegVideoRemuxer", "preferedformat": "mp4",
        })

    def test_cancel_does_not_start_download(self):
        with patch.object(downloading.filedialog, "asksaveasfilename", return_value=""), \
                patch.object(downloading.yt_dlp, "YoutubeDL") as downloader:
            downloading.download_audio("url", Mock())
        downloader.assert_not_called()


class TranscriptionTests(unittest.TestCase):
    def setUp(self):
        self.selection = patch.object(transcription, "selected_file_path", None)
        self.selection.start()
        self.addCleanup(self.selection.stop)

    def test_processing_before_selection_is_handled(self):
        label = Mock()
        transcription.process_transcription(label)
        self.assertEqual(label.config.call_args.kwargs["text"], "Please select a file first!")

    def test_empty_vocabulary_produces_empty_list(self):
        self.assertEqual(transcription.process_translations([]), [])

    def test_word_extraction_filters_numbers_and_deduplicates(self):
        self.assertEqual(transcription.get_unique_words_from_text("Hello hello WORLD! a 123 abc2 café"), ["hello", "world"])

    def test_dictionary_filtering(self):
        with patch.object(transcription.words, "words", return_value=["hello"]):
            self.assertEqual(transcription.get_unique_words_from_text("Hello worlds", use_dict=True), ["hello"])

    def test_transcription_failure_preserves_existing_output(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "words.txt"
            output.write_text("keep me", encoding="utf-8")
            transcription.selected_file_path = str(Path(directory) / "video.MP4")
            label = Mock()
            with patch.object(transcription.filedialog, "asksaveasfilename", return_value=str(output)), \
                    patch.object(transcription, "transcribe_audio", side_effect=RuntimeError("offline")):
                transcription.process_transcription(label)
            self.assertEqual(output.read_text(encoding="utf-8"), "keep me")
            self.assertEqual(list(Path(directory).iterdir()), [output])
            self.assertIn("Processing failed: offline", label.config.call_args.kwargs["text"])

    def test_empty_transcript_can_be_saved_and_uppercase_video_is_supported(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "words.txt"
            source = str(Path(directory) / "video.MP4")
            transcription.selected_file_path = source
            with patch.object(transcription.filedialog, "asksaveasfilename", return_value=str(output)), \
                    patch.object(transcription, "transcribe_audio", return_value="") as transcribe, \
                    patch.object(transcription.words, "words", return_value=[]):
                transcription.process_transcription(Mock())
            transcribe.assert_called_once_with(source)
            self.assertEqual(output.read_text(encoding="utf-8"), "")
            self.assertEqual(list(Path(directory).iterdir()), [output])

    def test_source_media_cannot_be_used_as_output(self):
        transcription.selected_file_path = "/tmp/source.mp3"
        label = Mock()
        with patch.object(transcription.filedialog, "asksaveasfilename", return_value="/tmp/source.mp3"), \
                patch.object(transcription, "transcribe_audio") as transcribe:
            transcription.process_transcription(label)
        transcribe.assert_not_called()
        self.assertIn("different from the source", label.config.call_args.kwargs["text"])

    def test_failed_save_cleans_temporary_file_and_preserves_existing_output(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "words.txt"
            output.write_text("keep me", encoding="utf-8")
            transcription.selected_file_path = str(Path(directory) / "audio.mp3")
            with patch.object(transcription.filedialog, "asksaveasfilename", return_value=str(output)), \
                    patch.object(transcription, "transcribe_audio", return_value="hello"), \
                    patch.object(transcription.words, "words", return_value=["hello"]), \
                    patch.object(transcription, "process_translations", return_value=["hello|həˈləʊ|привет\n"]), \
                    patch.object(transcription.os, "replace", side_effect=OSError("disk error")):
                transcription.process_transcription(Mock())
            self.assertEqual(output.read_text(encoding="utf-8"), "keep me")
            self.assertEqual(list(Path(directory).iterdir()), [output])

    def test_model_is_loaded_once_and_transcribes_english_media(self):
        transcription._load_model.cache_clear()
        model = Mock()
        model.transcribe.return_value = {"text": "hello"}
        with patch.object(transcription.whisper, "load_model", return_value=model) as load:
            self.assertEqual(transcription.transcribe_audio("first.mp3"), "hello")
            self.assertEqual(transcription.transcribe_audio("second.mp4"), "hello")
        load.assert_called_once_with("base")
        model.transcribe.assert_any_call("second.mp4", language="en")
        transcription._load_model.cache_clear()


if __name__ == "__main__":
    unittest.main()
