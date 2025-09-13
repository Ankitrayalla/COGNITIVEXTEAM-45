import io
import os
import tempfile
from typing import Optional
import pyttsx3
from pydub import AudioSegment

def list_voices() -> dict:
    """
    Return mapping {friendly_name: voice_id} of system voices available to pyttsx3.
    """
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    mapping = {}
    for v in voices:
        name = getattr(v, "name", None) or getattr(v, "id", "voice")
        mapping[name] = v.id
    return mapping

def synthesize_to_mp3_bytes(text: str, voice_id: Optional[str] = None, rate: int = 150) -> bytes:
    """
    Synthesize text to mp3 bytes using pyttsx3 -> temporary WAV -> pydub convert to MP3.
    """
    engine = pyttsx3.init()
    if voice_id:
        try:
            engine.setProperty("voice", voice_id)
        except Exception:
            pass
    engine.setProperty("rate", rate)

    # pyttsx3 writes to disk - create a temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_f:
        wav_path = wav_f.name

    engine.save_to_file(text, wav_path)
    engine.runAndWait()

    # Convert WAV -> MP3 in memory
    audio = AudioSegment.from_wav(wav_path)
    mp3_io = io.BytesIO()
    audio.export(mp3_io, format="mp3")
    mp3_io.seek(0)

    # cleanup
    try:
        os.remove(wav_path)
    except Exception:
        pass

    return mp3_io.read()
