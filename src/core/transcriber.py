import os
import math
import tempfile
from pathlib import Path
from pydub import AudioSegment
from dotenv import load_dotenv
from utils.logger import log_info, log_error
import whisper  # always import
from openai import OpenAI

load_dotenv()
openai_client = OpenAI()

MAX_SIZE_MB = 25
BUFFER_MB = 5
TARGET_MB = MAX_SIZE_MB - BUFFER_MB


def get_chunks(audio_path: str, target_mb: int = TARGET_MB):
    audio = AudioSegment.from_file(audio_path)
    size_bytes = os.path.getsize(audio_path)
    duration_ms = len(audio)
    bytes_per_ms = size_bytes / duration_ms
    chunk_duration_ms = math.floor((target_mb * 1024 * 1024) / bytes_per_ms)

    return [audio[i:i + chunk_duration_ms] for i in range(0, duration_ms, chunk_duration_ms)]


def transcribe_audio(audio_path: str, engine: str = "Whisper (local)") -> str:
    try:
        log_info(f"🧠 Transcribing using {engine}")

        if engine == "OpenAI Whisper":
            chunks = get_chunks(audio_path)
            full_text = ""

            for i, chunk in enumerate(chunks):
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    chunk.export(temp_file.name, format="mp3", bitrate="64k")
                    log_info(f"🔹 Transcribing chunk {i+1}/{len(chunks)}")

                    with open(temp_file.name, "rb") as f:
                        result = openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=f
                        )
                        full_text += result.text + "\n"

                    os.unlink(temp_file.name)

            return full_text.strip()

        elif engine == "Claude (summarize only)":
            raise NotImplementedError("Claude cannot transcribe audio directly.")

        else:  # "Whisper (local)"
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            return result["text"]

    except Exception as e:
        log_error(f"❌ Transcription failed: {e}")
        raise
