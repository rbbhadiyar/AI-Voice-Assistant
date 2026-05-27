# AI Voice Assistant

AI Voice Assistant is a Jarvis-style desktop web assistant that accepts voice or typed commands, sends them to an AI agent, and replies with spoken audio. It can answer general questions, search the web, calculate math, create notes, set reminders, open desktop apps or websites, and remember user preferences. The project uses a FastAPI backend with a simple browser frontend, so it can run locally without a complex build step.

## Tech Stack

- Python 3.10+
- FastAPI and Uvicorn for the backend API
- Groq Llama 3.1 model for AI responses and tool calling
- OpenAI Whisper for speech-to-text transcription
- gTTS for text-to-speech audio generation
- Tavily for real-time web search
- HTML, CSS, and JavaScript for the frontend
- FFmpeg for audio processing support

## Features

- Voice input through the browser microphone
- Text command input
- Spoken AI responses
- Real-time web search
- Notes, reminders, memory, and conversation history
- Desktop app and website opening commands
- One-command startup through `python main.py`

## Setup

1. Clone the repository:

```bash
git clone https://github.com/rbbhadiyar/AI-Voice-Assistant.git
cd AI-Voice-Assistant
```

2. Install FFmpeg.

On Windows, you can install it with:

```powershell
winget install ffmpeg
```

Restart the terminal after installation if FFmpeg is not detected immediately.

3. Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Note: the current code uses `gTTS` for speech output, but the startup check still expects `ELEVENLABS_API_KEY` to exist.

4. Start the project:

```bash
python main.py
```

The startup script installs backend dependencies, checks API keys, checks FFmpeg, starts the backend at `http://localhost:8000`, and opens `frontend/index.html`.

## API Endpoints

- `POST /voice` - accepts recorded audio and returns spoken AI response audio
- `POST /text` - accepts typed text and returns spoken AI response audio
- `GET /memory` - returns saved preferences, notes, reminders, and history
- `GET /notes` - returns saved notes
- `GET /reminders` - returns saved reminders
- `GET /history` - returns recent conversation history
- `GET /health` - checks whether the backend is running

## Screenshots

### Main Assistant Screen

The main screen lets the user hold the microphone button to speak, type commands manually, and use quick command buttons for common actions.

![Main assistant screen](Assets/Screenshot%202026-05-27%20222354.png)

### Assistant Data Views

The sidebar gives access to notes, reminders, memory, and conversation history so saved assistant data can be reviewed from the same interface.

![Assistant data views](Assets/Screenshot%202026-05-27%20222413.png)

## Video Demo

This demo shows the AI Voice Assistant running locally with its Jarvis-style interface. It demonstrates the main assistant screen, voice/text interaction flow, spoken responses, quick commands, and the supporting views for notes, reminders, memory, and conversation history.

Demo video:

https://github.com/user-attachments/assets/0bcbb42e-cf5a-4ce5-b18a-5ca654ea4447
