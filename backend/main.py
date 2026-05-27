from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from stt import transcribe_audio
from tts import text_to_speech
from agent import run_agent
from memory import add_history, get_memory, get_notes, get_reminders
import unicodedata, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

def safe_header(value: str) -> str:
    value = value.replace("\n", " ").replace("\r", " ")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\x20-\x7E]", "", value)
    return value[:500]

@app.post("/voice")
async def voice_endpoint(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    transcript = transcribe_audio(audio_bytes)
    response_text = run_agent(transcript)
    add_history(transcript, response_text)
    audio_response = text_to_speech(response_text)
    return Response(
        content=audio_response,
        media_type="audio/mpeg",
        headers={
            "X-Transcript": safe_header(transcript),
            "X-Response-Text": safe_header(response_text),
        }
    )

@app.post("/text")
async def text_endpoint(req: TextRequest):
    response_text = run_agent(req.text)
    add_history(req.text, response_text)
    audio_response = text_to_speech(response_text)
    return Response(
        content=audio_response,
        media_type="audio/mpeg",
        headers={
            "X-Transcript": safe_header(req.text),
            "X-Response-Text": safe_header(response_text),
        }
    )

@app.get("/memory")
async def memory_endpoint():
    return get_memory()

@app.get("/notes")
async def notes_endpoint():
    return get_notes()

@app.get("/reminders")
async def reminders_endpoint():
    return get_reminders()

@app.get("/history")
async def history_endpoint():
    mem = get_memory()
    return mem.get("history", [])

@app.get("/health")
async def health():
    return {"status": "ok"}
