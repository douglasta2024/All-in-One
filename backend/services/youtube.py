"""
YouTube metadata fetch and audio download via yt-dlp.
"""
import os
import yt_dlp

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", "tmp")


def fetch_metadata(url: str) -> dict:
    """Fetch video metadata without downloading anything."""
    opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title", ""),
        "uploader": info.get("uploader", ""),
        "description": info.get("description", ""),
        "webpage_url": info.get("webpage_url", url),
        "upload_date": info.get("upload_date", ""),
        "duration": info.get("duration", 0),
    }


def download_audio(url: str) -> str:
    """Download audio as mp3, return path to the file."""
    os.makedirs(TMP_DIR, exist_ok=True)
    output_template = os.path.join(TMP_DIR, "%(id)s.%(ext)s")
    opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id", "audio")

    return os.path.join(TMP_DIR, f"{video_id}.mp3")
