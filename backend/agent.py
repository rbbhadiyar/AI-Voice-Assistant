import os, json, re
from dotenv import load_dotenv
from groq import Groq
from tools.web_search import web_search
from tools.calculator import calculate
from tools.notes import create_note, list_notes
from tools.reminders import set_reminder, list_reminders
from tools.desktop import open_app
from memory import get_memory, add_preference

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

def _clean_response(text: str) -> str:
    text = re.sub(r'<function=.*', '', text, flags=re.DOTALL)
    text = re.sub(r'\(function=.*', '', text, flags=re.DOTALL)
    text = re.sub(r'\{\$assistant_response:.*', '', text, flags=re.DOTALL)
    return text.strip() or "I'm here to help! What can I do for you?"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information, news, weather, stock prices, or any real-time data.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate math expressions like '2+2', 'sqrt(16)', '15% of 200'.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Save a note with a title and content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "List all saved notes.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder with text and time/date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "when": {"type": "string"},
                },
                "required": ["text", "when"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "List all pending reminders.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a desktop app (notepad, calculator, chrome, etc.) or a website URL.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "App name or URL"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember_preference",
            "description": "Store a user preference like 'likes tech news' or 'timezone is IST'.",
            "parameters": {
                "type": "object",
                "properties": {"preference": {"type": "string"}},
                "required": ["preference"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_memory",
            "description": "Retrieve stored user preferences and context.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

def call_tool(name: str, args: dict) -> str:
    if name == "search_web":
        return web_search(args["query"])
    elif name == "calculator":
        return calculate(args["expression"])
    elif name == "create_note":
        return create_note(args["title"], args["content"])
    elif name == "list_notes":
        return list_notes()
    elif name == "set_reminder":
        return set_reminder(args["text"], args["when"])
    elif name == "list_reminders":
        return list_reminders()
    elif name == "open_app":
        return open_app(args["name"])
    elif name == "remember_preference":
        add_preference(args["preference"])
        return f"Got it! I'll remember that you {args['preference']}."
    elif name == "get_user_memory":
        mem = get_memory()
        prefs = ", ".join(mem["preferences"]) if mem["preferences"] else "none yet"
        return f"User preferences: {prefs}"
    return "Unknown tool"

def build_system_prompt() -> str:
    mem = get_memory()
    prefs = ", ".join(mem["preferences"]) if mem["preferences"] else "none"
    return (
        "You are Jarvis, an advanced AI voice assistant like Iron Man's Jarvis. "
        "Be concise, smart, and conversational. Keep responses voice-friendly (2-4 sentences). "
        "You can search the web, do math, take notes, set reminders, open apps, and remember preferences. "
        f"Known user preferences: {prefs}. "
        "Always use tools when the task requires real-time data, actions, or storage."
    )

def run_agent(user_input: str) -> str:
    messages = [{"role": "system", "content": build_system_prompt()}]

    # Inject recent history as proper alternating user/assistant messages
    mem = get_memory()
    for h in mem["history"][-4:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})

    messages.append({"role": "user", "content": user_input})

    while True:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            return _clean_response(response.choices[0].message.content)

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ],
            })
            for tc in msg.tool_calls:
                result = call_tool(tc.function.name, json.loads(tc.function.arguments))
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        else:
            return _clean_response(msg.content)
