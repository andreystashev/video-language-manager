# Video Language Manager

A small Tkinter desktop application for turning English audio and video into vocabulary lists. Download media with yt-dlp, transcribe a local MP3 or MP4 with OpenAI Whisper, and export unique English words with IPA pronunciation and Russian translations.

## Requirements

- Python 3.10–3.12 and Tkinter.
- The **FFmpeg command-line executable** on `PATH`. It is required by Whisper and by media conversion; a Python package named `ffmpeg` does not replace it.
- Internet access for media downloads, the first Whisper model download, NLTK corpus setup, and Google Translate requests through `deep-translator`.

Install FFmpeg with your operating system's package manager, for example `brew install ffmpeg` on macOS or `sudo apt install ffmpeg python3-tk python3-venv` on Debian/Ubuntu. On Windows, install FFmpeg and add its executable directory to `PATH`. Check it with `ffmpeg -version`.

## Setup and launch

```sh
git clone https://github.com/andreystashev/video-language-manager.git
cd video-language-manager
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m nltk.downloader words
python main.py
```

The Whisper distribution is **`openai-whisper`**. The unrelated package named `whisper` is not needed. The first transcription downloads the Whisper `base` model; later runs use its local cache.

## Use

1. In **Download**, enter a URL supported by yt-dlp and choose **Download Video** or **Download Audio Only**. Choose the destination in the save dialog. Audio is converted to MP3; video is merged or remuxed to MP4. Conversion can fail if the source codec cannot be placed in an MP4 container.
2. In **Process Media**, select a local MP3 or MP4. This is a separate step: downloads are not selected automatically.
3. Choose **Create Vocabulary List** and select a `.txt` destination.

The output is sorted alphabetically, with one word per line:

```text
word                             |IPA pronunciation                |Russian translation
```

Words are lowercase, unique, at least two letters long, and restricted to `a`–`z` entries in the NLTK English word corpus. Proper names, contractions, and specialist vocabulary may be omitted or split. A recording with no matching words produces an empty file.

Existing destination files are replaced only after a download or vocabulary export succeeds. Canceling or a failed processing step preserves the previous file.

## Limitations

- This is a synchronous desktop prototype: downloading, model inference, and translation run on the GUI thread and can temporarily make the window unresponsive.
- Transcription is configured for English; word translations target Russian. It does not translate subtitles or an entire transcript.
- Transcription runs locally, but each extracted word is sent to Google Translate. Availability and rate limits depend on that external service.
- yt-dlp support depends on the source website. If a supported URL stops working, try `python -m pip install --upgrade yt-dlp`.
- IPA and translation quality depend on the installed libraries and services. No packaged executable is included.

## Development checks

Run from the repository root. The isolated regression suite needs only Python
and Tkinter; the application dependencies, FFmpeg, models, and corpora are not
needed for these checks.

```sh
python -m unittest discover -s tests -v
python -m compileall -q main.py downloading.py transcription.py tests
```

The [Python checks workflow](.github/workflows/python-checks.yml) runs these
commands on Python 3.11 for pushes and pull requests.

Regression tests replace downloads, transcription, and translation with fakes. They cover file preservation, conversion options, empty input, word filtering, and processing errors without downloading a model or contacting external services. A desktop session and real media are still needed to validate the complete GUI workflow.
