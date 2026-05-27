import subprocess, webbrowser, os

APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "vs code": "code",
    "vscode": "code",
}

def open_app(name: str) -> str:
    key = name.lower().strip()
    if key.startswith("http://") or key.startswith("https://") or "." in key:
        webbrowser.open(key if key.startswith("http") else f"https://{key}")
        return f"Opened {key} in browser."
    if key in APPS:
        try:
            subprocess.Popen(APPS[key], shell=True)
            return f"Opened {name}."
        except Exception as e:
            return f"Could not open {name}: {e}"
    # Try opening as URL search
    webbrowser.open(f"https://www.google.com/search?q={name}")
    return f"Searched for '{name}' in browser."
