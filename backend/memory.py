import json, os
from datetime import datetime

MEMORY_FILE = "memory.json"

def _load() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return {"preferences": [], "history": [], "notes": [], "reminders": []}

def _save(data: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _migrate(data: dict) -> dict:
    data.setdefault("preferences", [])
    data.setdefault("history", [])
    data.setdefault("notes", [])
    data.setdefault("reminders", [])
    return data

def add_preference(pref: str):
    data = _migrate(_load())
    if pref not in data["preferences"]:
        data["preferences"].append(pref)
    _save(data)

import re as _re

def _clean(text: str) -> str:
    """Strip any leaked tool call syntax from a response before saving."""
    text = _re.sub(r'<function=.*', '', text, flags=_re.DOTALL)
    text = _re.sub(r'\(function=.*', '', text, flags=_re.DOTALL)
    text = _re.sub(r'\{\$assistant_response:.*', '', text, flags=_re.DOTALL)
    return text.strip()

def add_history(user: str, assistant: str):
    data = _migrate(_load())
    data["history"].append({
        "user": user,
        "assistant": _clean(assistant),
        "time": datetime.now().strftime("%H:%M")
    })
    data["history"] = data["history"][-30:]
    _save(data)

def add_note(title: str, content: str):
    data = _migrate(_load())
    data["notes"].append({
        "id": len(data["notes"]) + 1,
        "title": title,
        "content": content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    _save(data)

def get_notes() -> list:
    return _migrate(_load())["notes"]

def add_reminder(text: str, when: str):
    data = _migrate(_load())
    data["reminders"].append({
        "id": len(data["reminders"]) + 1,
        "text": text,
        "when": when,
        "done": False,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    _save(data)

def get_reminders() -> list:
    return _migrate(_load())["reminders"]

def get_memory() -> dict:
    return _migrate(_load())
