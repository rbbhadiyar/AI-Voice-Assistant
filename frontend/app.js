const API = "http://localhost:8000";

// Elements
const micBtn = document.getElementById("micBtn");
const micLabel = document.getElementById("micLabel");
const micRings = document.getElementById("micRings");
const textInput = document.getElementById("textInput");
const sendBtn = document.getElementById("sendBtn");
const responseCard = document.getElementById("responseCard");
const transcriptEl = document.getElementById("transcriptEl");
const responseText = document.getElementById("responseText");
const playingBar = document.getElementById("playingBar");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

let mediaRecorder, audioChunks = [], isRecording = false;

// --- Tab navigation ---
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    if (btn.dataset.tab === "notes") loadNotes();
    if (btn.dataset.tab === "reminders") loadReminders();
    if (btn.dataset.tab === "memory") loadMemory();
    if (btn.dataset.tab === "history") loadHistory();
  });
});

// --- Quick commands ---
document.querySelectorAll(".qbtn").forEach(btn => {
  btn.addEventListener("click", () => {
    textInput.value = btn.dataset.cmd;
    sendText();
  });
});

// --- Mic recording ---
micBtn.addEventListener("mousedown", startRecording);
micBtn.addEventListener("mouseup", stopRecording);
micBtn.addEventListener("touchstart", e => { e.preventDefault(); startRecording(); });
micBtn.addEventListener("touchend", e => { e.preventDefault(); stopRecording(); });

async function startRecording() {
  if (isRecording) return;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.start();
    isRecording = true;
    micBtn.classList.add("recording");
    micRings.classList.add("active");
    micLabel.textContent = "Listening...";
    setStatus("🔴 Listening", "busy");
  } catch {
    setStatus("❌ Mic denied", "error");
  }
}

function stopRecording() {
  if (!isRecording || !mediaRecorder) return;
  mediaRecorder.stop();
  isRecording = false;
  micBtn.classList.remove("recording");
  micBtn.classList.add("loading");
  micRings.classList.remove("active");
  micLabel.textContent = "Processing...";
  setStatus("⏳ Thinking", "busy");

  mediaRecorder.onstop = async () => {
    const blob = new Blob(audioChunks, { type: "audio/webm" });
    await sendAudio(blob);
    mediaRecorder.stream.getTracks().forEach(t => t.stop());
  };
}

async function sendAudio(blob) {
  const form = new FormData();
  form.append("audio", blob, "recording.webm");
  try {
    const res = await fetch(`${API}/voice`, { method: "POST", body: form });
    await handleResponse(res);
  } catch (err) {
    setStatus("❌ " + err.message, "error");
  } finally {
    resetMic();
  }
}

// --- Text input ---
sendBtn.addEventListener("click", sendText);
textInput.addEventListener("keydown", e => { if (e.key === "Enter") sendText(); });

async function sendText() {
  const text = textInput.value.trim();
  if (!text) return;
  textInput.value = "";
  setStatus("⏳ Thinking", "busy");
  sendBtn.disabled = true;
  try {
    const res = await fetch(`${API}/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    await handleResponse(res);
  } catch (err) {
    setStatus("❌ " + err.message, "error");
  } finally {
    sendBtn.disabled = false;
  }
}

// --- Handle response ---
async function handleResponse(res) {
  if (!res.ok) { setStatus("❌ Server error", "error"); return; }

  const transcript = res.headers.get("X-Transcript") || "";
  const response = res.headers.get("X-Response-Text") || "";
  const audioBlob = await res.blob();

  transcriptEl.textContent = transcript ? `You: "${transcript}"` : "";
  responseText.textContent = response;
  responseCard.style.display = "flex";

  playAudio(audioBlob);
  setStatus("✅ Ready", "");
  loadMemory();
}

function playAudio(blob) {
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  playingBar.style.display = "flex";
  audio.play().catch(() => {});
  audio.onended = () => {
    playingBar.style.display = "none";
    URL.revokeObjectURL(url);
  };
}

function resetMic() {
  micBtn.classList.remove("loading");
  micLabel.textContent = "Hold to Speak";
}

function setStatus(msg, state) {
  statusText.textContent = msg;
  statusDot.className = "dot" + (state ? " " + state : "");
}

// --- Data loaders ---
async function loadNotes() {
  const el = document.getElementById("notesList");
  try {
    const res = await fetch(`${API}/notes`);
    const notes = await res.json();
    if (!notes.length) { el.innerHTML = `<div class="empty-state">No notes yet. Say "Take a note: title — content"</div>`; return; }
    el.innerHTML = notes.reverse().map(n => `
      <div class="card-item">
        <div class="card-title">${n.title}</div>
        <div class="card-body">${n.content}</div>
        <div class="card-meta">${n.time}</div>
      </div>`).join("");
  } catch { el.innerHTML = `<div class="empty-state">Could not load notes.</div>`; }
}

async function loadReminders() {
  const el = document.getElementById("remindersList");
  try {
    const res = await fetch(`${API}/reminders`);
    const reminders = await res.json();
    if (!reminders.length) { el.innerHTML = `<div class="empty-state">No reminders yet. Say "Remind me to [task] at [time]"</div>`; return; }
    el.innerHTML = reminders.reverse().map(r => `
      <div class="card-item">
        <div class="card-title">${r.done ? "✅" : "⏳"} ${r.text}</div>
        <div class="card-body">When: ${r.when}</div>
        <div class="card-meta">Set at ${r.time}</div>
      </div>`).join("");
  } catch { el.innerHTML = `<div class="empty-state">Could not load reminders.</div>`; }
}

async function loadMemory() {
  const el = document.getElementById("memoryList");
  try {
    const res = await fetch(`${API}/memory`);
    const data = await res.json();
    const prefs = data.preferences || [];
    if (!prefs.length) { el.innerHTML = `<div class="empty-state">No preferences yet. Say "Remember I like [topic]"</div>`; return; }
    el.innerHTML = prefs.map(p => `
      <div class="card-item">
        <div class="card-body">🧠 ${p}</div>
      </div>`).join("");
  } catch { el.innerHTML = `<div class="empty-state">Could not load memory.</div>`; }
}

async function loadHistory() {
  const el = document.getElementById("historyList");
  try {
    const res = await fetch(`${API}/history`);
    const history = await res.json();
    if (!history.length) { el.innerHTML = `<div class="empty-state">No conversation history yet.</div>`; return; }
    el.innerHTML = history.reverse().map(h => `
      <div class="history-item">
        <div class="history-user"><span>You</span> · ${h.time || ""}</div>
        <div class="history-user">${h.user}</div>
        <div class="history-assistant"><span>Jarvis</span></div>
        <div class="history-assistant">${h.assistant}</div>
      </div>`).join("");
  } catch { el.innerHTML = `<div class="empty-state">Could not load history.</div>`; }
}

// Init
loadMemory();
