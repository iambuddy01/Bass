import asyncio
import os
import ffmpeg
from pyrogram import Client, filters
from py_tgcalls import PyTgCalls, idle, AudioPiped
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# ----------------------------
# Telegram Bot
# ----------------------------
bot = Client(
    "BassBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ----------------------------
# Assistant Client (userbot)
# ----------------------------
assistant = Client(
    name="assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

pytgcalls = PyTgCalls(assistant)
active_sessions = {}  # chat_id -> file_path

# ----------------------------
# Bass Boost Function
# ----------------------------
def apply_bass_boost(input_file: str) -> str:
    boosted_file = f"boosted_{os.path.basename(input_file)}"
    try:
        (
            ffmpeg
            .input(input_file)
            .output(
                boosted_file,
                af='bass=g=25:f=80,volume=10dB',
                format='wav',
                acodec='pcm_s16le',
                ac=2,
                ar='44100'
            )
            .overwrite_output()
            .run(quiet=True)
        )
        return boosted_file
    except Exception as e:
        print(f"[BassFilterError] {e}")
        return input_file

# ----------------------------
# Play Audio in VC
# ----------------------------
async def play_bass(file_path: str, chat_id: int):
    try:
        await assistant.join_chat(chat_id)
    except:
        pass

    boosted_file = apply_bass_boost(file_path)
    active_sessions[chat_id] = boosted_file

    try:
        await pytgcalls.join_group_call(
            chat_id,
            AudioPiped(boosted_file)
        )
    except Exception as e:
        print(f"[BassError] {e}")

@pytgcalls.on_stream_end()
async def restart_stream(_, update):
    chat_id = update.chat_id
    if chat_id in active_sessions:
        file = active_sessions[chat_id]
        await asyncio.sleep(2)
        await play_bass(file, chat_id)

async def stop_bass(chat_id: int):
    try:
        await pytgcalls.leave_group_call(chat_id)
    except:
        pass
    if chat_id in active_sessions:
        file = active_sessions.pop(chat_id)
        try:
            os.remove(file)
        except:
            pass

# ----------------------------
# /start and alive message
# ----------------------------
@bot.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply_text("🎵 BassBot is alive! Send /bass to start a looped extreme bass track.")

# ----------------------------
# /bass command
# ----------------------------
user_uploads = {}  # user_id -> file_path

@bot.on_message(filters.command("bass") & filters.private)
async def bass_cmd(client: Client, message: Message):
    await message.reply_text("Send me the audio file or voice message you want to play in VC.")

@bot.on_message(filters.voice | filters.audio)
async def save_audio(client: Client, message: Message):
    file_path = await message.download()
    user_uploads[message.from_user.id] = file_path
    await message.reply_text("Audio received! Now send me the target Telegram Group ID.")

@bot.on_message(filters.text & filters.private)
async def receive_group_id(client: Client, message: Message):
    if message.from_user.id not in user_uploads:
        return
    try:
        chat_id = int(message.text)
    except ValueError:
        await message.reply_text("❌ Invalid ID. Send a numeric Telegram group ID.")
        return
    file_path = user_uploads.pop(message.from_user.id)
    await play_bass(file_path, chat_id)
    await message.reply_text(f"✅ Started playing in group `{chat_id}` with extreme bass.")

# ----------------------------
# /bstop command
# ----------------------------
@bot.on_message(filters.command("bstop") & filters.private)
async def stop_cmd(client: Client, message: Message):
    await stop_bass(int(message.text))
    await message.reply_text("⏹ Playback stopped.")

# ----------------------------
# Run everything
# ----------------------------
async def main():
    await bot.start()
    await assistant.start()
    await pytgcalls.start()
    print("[BassBot] Running with extreme bass 🔊")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
