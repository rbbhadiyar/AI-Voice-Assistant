from memory import add_note, get_notes

def create_note(title: str, content: str) -> str:
    add_note(title, content)
    return f"Note '{title}' saved successfully."

def list_notes() -> str:
    notes = get_notes()
    if not notes:
        return "No notes saved yet."
    return "\n".join([f"[{n['id']}] {n['title']}: {n['content']}" for n in notes[-5:]])
