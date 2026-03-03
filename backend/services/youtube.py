"""
YouTube metadata fetch via yt-dlp.
"""
import yt_dlp


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
