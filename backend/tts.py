from gtts import gTTS
import tempfile, os

def text_to_speech(text: str) -> bytes:
    tts = gTTS(text=text, lang="en", slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name
    try:
        tts.save(tmp_path)
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp_path)
