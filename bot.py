import os
import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")

if not DISCORD_TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN environment variable")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is online. Type !ask <your prompt> in Discord.")


@bot.command(name="ask")
async def ask_chatgpt(ctx: commands.Context, *, prompt: str):
    """Use: !ask your question"""
    await ctx.trigger_typing()

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )
        answer = response.output_text.strip()
    except Exception as e:
        await ctx.reply(f"Error from OpenAI API: {e}")
        return

    if not answer:
        answer = "I couldn't generate a response this time."

    # Discord message limit is 2000 chars
    chunks = [answer[i : i + 1900] for i in range(0, len(answer), 1900)] or [answer]
    for i, chunk in enumerate(chunks):
        if i == 0:
            await ctx.reply(chunk)
        else:
            await ctx.send(chunk)


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.reply("Pong! ✅")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
