"""
Local audio transcription using OpenAI Whisper.
"""
import os
import whisper

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file, return full transcript text."""
    model = _get_model()
    result = model.transcribe(audio_path, language="en", fp16=False)
    # Clean up tmp file after transcription
    try:
        os.remove(audio_path)
    except OSError:
        pass
    return result["text"].strip()
