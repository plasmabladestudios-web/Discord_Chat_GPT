from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# Lightweight in-memory storage for demo/dev purposes.
users: Dict[str, dict] = {}
conversations: Dict[str, dict] = {
    "global": {
        "id": "global",
        "name": "Community",
        "participants": [],
        "messages": [],
        "is_group": True,
    }
}
statuses: List[dict] = []


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/register")
def register_user():
    payload = request.get_json(force=True)
    user_id = payload.get("user_id") or str(uuid.uuid4())
    profile = {
        "id": user_id,
        "name": payload.get("name", "Anonymous"),
        "bio": payload.get("bio", "Available"),
        "avatar": payload.get("avatar", "🟢"),
        "accent": payload.get("accent", "#25d366"),
        "theme": payload.get("theme", "dark"),
        "wallpaper": payload.get("wallpaper", "none"),
        "bubble_radius": payload.get("bubble_radius", 14),
    }
    users[user_id] = profile
    if user_id not in conversations["global"]["participants"]:
        conversations["global"]["participants"].append(user_id)
    return jsonify(profile)


@app.get("/api/bootstrap")
def bootstrap():
    user_id = request.args.get("user_id", "")
    active_statuses = []
    now = datetime.now(timezone.utc)
    for status in statuses:
        created = datetime.fromisoformat(status["created_at"])
        if now - created < timedelta(hours=24):
            active_statuses.append(status)

    visible_conversations = []
    for convo in conversations.values():
        if convo["is_group"] or user_id in convo["participants"]:
            visible_conversations.append(convo)

    return jsonify(
        {
            "user": users.get(user_id),
            "users": list(users.values()),
            "conversations": visible_conversations,
            "statuses": active_statuses,
        }
    )


@app.post("/api/conversations")
def create_conversation():
    payload = request.get_json(force=True)
    convo_id = str(uuid.uuid4())
    participants = payload.get("participants", [])
    convo = {
        "id": convo_id,
        "name": payload.get("name", "Direct Chat"),
        "participants": participants,
        "messages": [],
        "is_group": bool(payload.get("is_group", False)),
    }
    conversations[convo_id] = convo
    return jsonify(convo), 201


@app.post("/api/status")
def post_status():
    payload = request.get_json(force=True)
    status = {
        "id": str(uuid.uuid4()),
        "user_id": payload["user_id"],
        "text": payload.get("text", ""),
        "created_at": utc_now_iso(),
    }
    statuses.append(status)
    socketio.emit("status:new", status)
    return jsonify(status), 201


@socketio.on("join")
def on_join(data):
    room = data.get("room", "global")
    join_room(room)
    emit("system", {"message": f"Joined {room}"})


@socketio.on("leave")
def on_leave(data):
    room = data.get("room", "global")
    leave_room(room)


@socketio.on("message:send")
def on_message_send(data):
    convo_id = data.get("conversation_id", "global")
    if convo_id not in conversations:
        return

    msg = {
        "id": str(uuid.uuid4()),
        "conversation_id": convo_id,
        "sender_id": data.get("sender_id"),
        "text": data.get("text", ""),
        "created_at": utc_now_iso(),
    }
    conversations[convo_id]["messages"].append(msg)
    emit("message:new", msg, room=convo_id)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
