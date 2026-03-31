# GPT Discord Bot

A simple Discord bot named **GPT** that lets you chat with ChatGPT inside your Discord server.

## 1) Create the Discord bot (name it `GPT`)

1. Open the Discord Developer Portal: https://discord.com/developers/applications
2. Click **New Application** and set the name to **GPT**.
3. Go to **Bot** → **Add Bot**.
4. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
5. Copy the **bot token**.

## 2) Invite GPT bot to your server

1. In the Developer Portal, go to **OAuth2** → **URL Generator**.
2. Select scopes:
   - `bot`
3. Select bot permissions:
   - Send Messages
   - Read Message History
   - View Channels
4. Open the generated URL and add the bot to your server.

## 3) Set up and run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and add your tokens.

Run:

```bash
export $(grep -v '^#' .env | xargs)
python bot.py
```

## 4) Use the bot

In Discord:

- `!ping` → health check
- `!ask Explain black holes simply` → get an AI answer

## 5) Keep GPT online 24/7

### Option A: Railway / Render / Koyeb (easy)

1. Push this project to GitHub.
2. Create a new service on Railway/Render/Koyeb from your repo.
3. Set environment variables:
   - `DISCORD_TOKEN`
   - `OPENAI_API_KEY`
   - optional: `OPENAI_MODEL`
4. Start command:
   - `python bot.py`
5. Deploy. The platform keeps it running continuously.

### Option B: VPS + systemd (stable)

On Ubuntu server, create service file `/etc/systemd/system/gpt-discord-bot.service`:

```ini
[Unit]
Description=GPT Discord Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Discord_Chat_GPT
Environment="DISCORD_TOKEN=your_discord_bot_token"
Environment="OPENAI_API_KEY=your_openai_api_key"
Environment="OPENAI_MODEL=gpt-4o-mini"
ExecStart=/home/ubuntu/Discord_Chat_GPT/.venv/bin/python /home/ubuntu/Discord_Chat_GPT/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gpt-discord-bot
sudo systemctl start gpt-discord-bot
sudo systemctl status gpt-discord-bot
```

Your bot will auto-restart on crash and reboot.

## Notes

- Keep your keys secret.
- For busy servers, add per-user rate limits and moderation checks.
