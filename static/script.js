const socket = io();
let currentUser = JSON.parse(localStorage.getItem("chatwave-user") || "null");
let conversationId = "global";

const el = (id) => document.getElementById(id);
const messagesEl = el("messages");

function applyUi(profile) {
  if (!profile) return;
  document.body.dataset.theme = profile.theme || "dark";
  document.body.style.setProperty("--accent", profile.accent || "#25d366");
  document.body.style.setProperty("--bubble-radius", `${profile.bubble_radius || 14}px`);
  messagesEl.classList.remove("wallpaper-grid", "wallpaper-waves");
  if (profile.wallpaper === "grid") messagesEl.classList.add("wallpaper-grid");
  if (profile.wallpaper === "waves") messagesEl.classList.add("wallpaper-waves");
}

function renderMessage(msg) {
  const item = document.createElement("div");
  item.className = "bubble" + (msg.sender_id === currentUser?.id ? " mine" : "");
  item.textContent = msg.text;
  messagesEl.appendChild(item);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderStatuses(statuses, users = []) {
  const userMap = Object.fromEntries(users.map((u) => [u.id, u]));
  const feed = el("status-feed");
  feed.innerHTML = "";
  statuses.forEach((s) => {
    const li = document.createElement("li");
    const author = userMap[s.user_id]?.name || "Unknown";
    li.textContent = `${author}: ${s.text}`;
    feed.appendChild(li);
  });
}

async function bootstrap() {
  const userId = currentUser?.id || "";
  const res = await fetch(`/api/bootstrap?user_id=${encodeURIComponent(userId)}`);
  const data = await res.json();

  if (data.user) {
    currentUser = data.user;
    localStorage.setItem("chatwave-user", JSON.stringify(currentUser));
    applyUi(currentUser);
  }

  const global = data.conversations.find((c) => c.id === "global");
  (global?.messages || []).forEach(renderMessage);
  renderStatuses(data.statuses, data.users);
}

el("save-profile").addEventListener("click", async () => {
  const payload = {
    user_id: currentUser?.id,
    name: el("name").value || "Anonymous",
    bio: el("bio").value || "Available",
    avatar: el("avatar").value || "🙂",
    accent: el("accent").value,
    theme: el("theme").value,
    wallpaper: el("wallpaper").value,
    bubble_radius: Number(el("bubble-radius").value),
  };

  const res = await fetch("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  currentUser = await res.json();
  localStorage.setItem("chatwave-user", JSON.stringify(currentUser));
  applyUi(currentUser);
  socket.emit("join", { room: conversationId });
});

el("apply-ui").addEventListener("click", () => {
  if (!currentUser) return;
  currentUser.theme = el("theme").value;
  currentUser.wallpaper = el("wallpaper").value;
  currentUser.accent = el("accent").value;
  currentUser.bubble_radius = Number(el("bubble-radius").value);
  applyUi(currentUser);
});

el("send-message").addEventListener("click", () => {
  if (!currentUser) {
    alert("Save your profile first.");
    return;
  }
  const text = el("message-input").value.trim();
  if (!text) return;
  socket.emit("message:send", {
    conversation_id: conversationId,
    sender_id: currentUser.id,
    text,
  });
  el("message-input").value = "";
});

el("post-status").addEventListener("click", async () => {
  if (!currentUser) {
    alert("Save your profile first.");
    return;
  }
  const text = el("status-input").value.trim();
  if (!text) return;

  await fetch("/api/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: currentUser.id, text }),
  });
  el("status-input").value = "";
});

socket.on("connect", () => {
  socket.emit("join", { room: conversationId });
});

socket.on("message:new", (msg) => {
  if (msg.conversation_id === conversationId) renderMessage(msg);
});

socket.on("status:new", async () => {
  const res = await fetch(`/api/bootstrap?user_id=${encodeURIComponent(currentUser?.id || "")}`);
  const data = await res.json();
  renderStatuses(data.statuses, data.users);
});

bootstrap();
