from memory import add_reminder, get_reminders

def set_reminder(text: str, when: str) -> str:
    add_reminder(text, when)
    return f"Reminder set: '{text}' for {when}."

def list_reminders() -> str:
    reminders = get_reminders()
    if not reminders:
        return "No reminders set."
    pending = [r for r in reminders if not r["done"]]
    if not pending:
        return "All reminders are done!"
    return "\n".join([f"[{r['id']}] {r['text']} — {r['when']}" for r in pending])
