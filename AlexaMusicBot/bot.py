import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL

API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytg = PyTgCalls(app)

ydl_opts = {"format": "bestaudio", "noplaylist": True}

async def stream_yt(chat_id: int, url: str):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]
    await pytg.join_group_call(chat_id, InputStream(AudioPiped(audio_url)))

@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("🎵 Alexa Music Bot is Online!")

@app.on_message(filters.command("play") & filters.reply)
async def play(_, msg):
    if msg.reply_to_message.audio:
        file = await msg.reply_to_message.download()
        await pytg.join_group_call(msg.chat.id, InputStream(AudioPiped(file)))
        await msg.reply("▶️ Playing downloaded Telegram audio...")
    else:
        # Fallback to search query
        query = msg.text.split(maxsplit=1)[-1]
        with YoutubeDL(ydl_opts) as ydl:
            try:
                results = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"]
                if not results:
                    await msg.reply("❌ No results found on YouTube.")
                    return
                info = results[0]
                audio_url = info["url"]
                await pytg.join_group_call(msg.chat.id, InputStream(AudioPiped(audio_url)))
                await msg.reply(f"▶️ Now playing: {info.get('title', 'Unknown')}")
            except Exception as e:
                await msg.reply(f"❌ Failed to play: {e}")
        url = msg.text.split(maxsplit=1)[-1]
        await stream_yt(msg.chat.id, url)
        await msg.reply("▶️ Streaming YouTube audio...")

async def start_bot():
    await app.start()
    await pytg.start()
    print("🤖 AlexaMusicBot Started")
    await asyncio.Event().wait()
