import subprocess
from pathlib import Path
from utils.logger import log_info, log_error
import sys
from moviepy import VideoFileClip
from pathlib import Path
from utils.logger import log_info, log_error
import re
from yt_dlp import YoutubeDL



def sanitize_filename(title: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', title)
    return re.sub(r'_+', '_', sanitized)  # collapse repeated underscores


def download_youtube_video(url: str, progress_callback=None) -> str:
    log_info(f"🔗 Download started")

    output_dir = Path("downloads")
    output_dir.mkdir(exist_ok=True)

    def hook(d):
        if d.get('status') == 'downloading':
            if 'downloaded_bytes' in d and ('total_bytes' in d or 'total_bytes_estimate' in d):
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
                try:
                    percent = int(d['downloaded_bytes'] / total * 100)
                    if progress_callback:
                        progress_callback(percent)
                except ZeroDivisionError:
                    pass
        elif d.get('status') == 'finished':
            if progress_callback:
                progress_callback(100)


    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': str(output_dir / '%(title).30s.%(ext)s'),
            'quiet': True,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'progress_hooks': [hook],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            log_info(f"✅ Download complete: {filename}")
            return filename

    except Exception as e:
        log_error(f"❌ YouTube download failed: {e}")
        raise



def extract_audio(video_path: str, progress_callback=None) -> str:
    try:
        log_info(f"🎞 Extracting audio from: {video_path}")
        clip = VideoFileClip(video_path)

        output_dir = Path("temp")
        output_dir.mkdir(exist_ok=True)
        audio_path = output_dir / (Path(video_path).stem + ".wav")

        clip.audio.write_audiofile(audio_path, codec='pcm_s16le')

        if progress_callback:
            progress_callback(100)  # ✅ Ses başarıyla çıkarıldıysa progress 100 yap

        log_info(f"✅ Audio extracted to: {audio_path}")
        return str(audio_path)
    except Exception as e:
        log_error(f"❌ Audio extraction failed: {e}")
        raise

