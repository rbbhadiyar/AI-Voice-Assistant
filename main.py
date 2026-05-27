import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend" / "index.html"
ENV_FILE = ROOT / ".env"


def check_env():
    if not ENV_FILE.exists():
        print("❌ .env file not found. Please create it with your API keys.")
        sys.exit(1)
    content = ENV_FILE.read_text()
    missing = []
    for key in ["GROQ_API_KEY", "ELEVENLABS_API_KEY", "TAVILY_API_KEY"]:
        if f"{key}=your_" in content or f"{key}=" not in content:
            missing.append(key)
    if missing:
        print(f"❌ Please fill in these keys in .env: {', '.join(missing)}")
        sys.exit(1)
    print("✅ API keys found")


FFMPEG_WINGET_PATH = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"

def find_ffmpeg_bin() -> str:
    """Search winget packages folder for ffmpeg bin directory."""
    if FFMPEG_WINGET_PATH.exists():
        for folder in FFMPEG_WINGET_PATH.glob("Gyan.FFmpeg*"):
            for bin_dir in folder.rglob("bin"):
                if (bin_dir / "ffmpeg.exe").exists():
                    return str(bin_dir)
    return ""

def check_ffmpeg():
    result = subprocess.run("ffmpeg -version", shell=True, capture_output=True)
    if result.returncode == 0:
        print("✅ ffmpeg found")
        return

    # Try to auto-add winget-installed ffmpeg to PATH
    bin_path = find_ffmpeg_bin()
    if bin_path:
        os.environ["PATH"] = bin_path + os.pathsep + os.environ.get("PATH", "")
        print(f"✅ ffmpeg auto-detected at: {bin_path}")
        return

    print("❌ ffmpeg not found. Run: winget install ffmpeg")
    print("   Then restart this terminal and try again.")
    sys.exit(1)


def install_requirements():
    req_file = BACKEND / "requirements.txt"
    print("📦 Checking dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "-q"],
        check=True
    )
    print("✅ Dependencies ready")


def open_browser():
    time.sleep(2)
    webbrowser.open(str(FRONTEND))
    print(f"🌐 Opened frontend: {FRONTEND}")


def start_backend():
    print("🚀 Starting Jarvis backend on http://localhost:8000 ...")
    env = os.environ.copy()  # already has ffmpeg PATH from check_ffmpeg()
    env["PYTHONPATH"] = str(BACKEND)

    # Load .env into environment
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

    subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(BACKEND),
        env=env
    )


if __name__ == "__main__":
    print("\n🎙️  Jarvis — AI Voice Assistant\n" + "=" * 35)
    check_env()
    check_ffmpeg()
    install_requirements()

    threading.Thread(target=open_browser, daemon=True).start()
    start_backend()
