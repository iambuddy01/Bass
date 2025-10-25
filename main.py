import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pydub import AudioSegment
from py-tgcalls import PyTgCalls, idle, AudioPiped

from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# ==============================
# 🔹 Bot & Assistant Client
# ==============================
bot = Client(
    "BassBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

assistant = Client(
    name="assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

pytgcalls = PyTgCalls(assistant)
active_sessions = {}  # chat_id -> file_path

# ==============================
# 🔊 Bass Boost Function
# ==============================
def apply_bass_boost(audio_path: str) -> str:
    audio = AudioSegment.from_file(audio_path)
    # Extreme bass: low pass + high pass + huge gain
    boosted = audio.low_pass_filter(250).high_pass_filter(100).apply_gain(40)
    boosted_path = "boosted_audio.mp3"  # always overwrite
    boosted.export(boosted_path, format="mp3")
    return boosted_path

# ==============================
# 🎧 Play in VC
# ==============================
async def play_bass(file_path: str, chat_id: int):
    boosted_file = apply_bass_boost(file_path)
    active_sessions[chat_id] = boosted_file

    try:
        await assistant.join_chat(chat_id)
    except:
        pass

    try:
        await pytgcalls.join_group_call(chat_id, AudioPiped(boosted_file))
    except Exception as e:
        print(f"[BassError] {e}")

@pytgcalls.on_stream_end()
async def loop_audio(_, update):
    chat_id = update.chat_id
    if chat_id in active_sessions:
        await asyncio.sleep(1)
        await play_bass(active_sessions[chat_id], chat_id)

async def stop_bass(chat_id: int):
    try:
        await pytgcalls.leave_group_call(chat_id)
    except:
        pass
    if chat_id in active_sessions:
        try:
            os.remove(active_sessions.pop(chat_id))
        except:
            pass

# ==============================
# 💬 Bot Commands
# ==============================
@bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply_text(
        "🎵 **Bass Bot is alive!**\n"
        "Use /bass to send an audio file or voice message to play with extreme bass."
    )

user_audio_files = {}  # user_id -> audio_path

@bot.on_message(filters.command("bass") & filters.reply)
async def bass_cmd(client, message: Message):
    try:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            file_path = await client.download_media(message.reply_to_message)
            user_audio_files[message.from_user.id] = file_path
            await message.reply_text("✅ Audio received! Now send the target **group ID** where I should play it.")
        else:
            await message.reply_text("🚫 Reply to an audio or voice message with /bass.")
    except Exception as e:
        await message.reply_text(f"🚫 Error: {e}")

@bot.on_message(filters.text)
async def receive_group_id(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_audio_files:
        try:
            chat_id = int(message.text.strip())
            file_path = user_audio_files[user_id]
            await play_bass(file_path, chat_id)
            await message.reply_text(f"🎧 Playing audio with extreme bass in VC: `{chat_id}`")
            del user_audio_files[user_id]
        except Exception as e:
            await message.reply_text(f"🚫 Failed: {e}")

@bot.on_message(filters.command("bstop"))
async def stop_cmd(client, message: Message):
    await stop_bass(int(message.text.split(" ")[1]) if len(message.text.split()) > 1 else 0)
    await message.reply_text("⏹️ Playback stopped.")

# ==============================
# 🔹 Run Assistant + Bot
# ==============================
async def run():
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    print("[BassBot] Running with Extreme Bass 🔊")
    await idle()

if __name__ == "__main__":
    asyncio.run(run())
