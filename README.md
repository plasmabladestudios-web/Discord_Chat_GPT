# ChatWave (WhatsApp-inspired Chat Application)

A real-time chat web app inspired by WhatsApp, including:

- Real-time messaging (Socket.IO)
- Status updates that act like 24-hour stories
- Customizable profile (name, bio, avatar emoji)
- Customizable UI (theme, accent color, wallpaper, bubble radius)

## Features

### 1) Real-time chat
- Live message delivery in the community room
- Message bubbles aligned by sender

### 2) Status feature
- Post short status messages
- Statuses are visible in a dedicated panel
- Back-end keeps only statuses from the last 24 hours

### 3) Customizable profile
- Name
- Bio
- Avatar emoji

### 4) Customizable UI
- Dark/light themes
- Accent color picker
- Wallpaper presets (none/grid/waves)
- Bubble radius slider

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: http://localhost:5000

## Notes

- Data is in-memory for demo purposes (restarts clear users/messages/statuses).
- For production, connect to a database and add authentication.
