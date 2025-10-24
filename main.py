import asyncio
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from assistant import run_assistant, play_bass, stop_bass
import os

bot = Client(
    "BassBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

user_sessions = {}  # user_id -> {"file": ..., "chat_id": ...}

# ==============================
# /start command
# ==============================
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply(
        "🎵 **Bass Bot is Alive!**\n\n"
        "Commands available:\n"
        "• `/bass` - Send audio/voice to play in a group VC\n"
        "• `/bstop` - Stop the currently playing audio\n\n"
        "Send `/bass` to get started!"
    )

# ==============================
# /bass command
# ==============================
@bot.on_message(filters.command("bass") & filters.private)
async def bass_cmd(client, message):
    await message.reply("Send me the audio file or voice note to play in VC.")

    @bot.on_message(filters.audio | filters.voice & filters.private)
    async def receive_audio(client, audio_msg):
        file_path = await audio_msg.download()
        user_sessions[message.from_user.id] = {"file": file_path}
        await audio_msg.reply("Got it! Now send the Telegram group ID where I should play this audio.")
        
        @bot.on_message(filters.text & filters.private)
        async def receive_chat_id(client, chat_msg):
            chat_id = int(chat_msg.text)
            user_sessions[message.from_user.id]["chat_id"] = chat_id
            await chat_msg.reply("Joining the group VC and playing your audio...")
            await play_bass(file_path, chat_id)
            # unregister after use
            bot.remove_handler(receive_chat_id)
            bot.remove_handler(receive_audio)

# ==============================
# /bstop command
# ==============================
@bot.on_message(filters.command("bstop") & filters.private)
async def bstop_cmd(client, message):
    session = user_sessions.get(message.from_user.id)
    if session:
        await stop_bass(session["chat_id"])
        await message.reply("Stopped playback.")
        # cleanup
        try: os.remove(session["file"])
        except: pass
        user_sessions.pop(message.from_user.id, None)
    else:
        await message.reply("No active playback found.")

# ==============================
# Start bot + assistant
# ==============================
async def main():
    await bot.start()
    print("[BassBot] Running...")
    await run_assistant()
    await bot.idle()

if __name__ == "__main__":
    asyncio.run(main())
