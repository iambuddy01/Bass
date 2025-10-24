import asyncio
import os
import ffmpeg
from pyrogram import Client, filters
from py_tgcalls import PyTgCalls, idle, AudioPiped
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# -----------------------------
# Create bot client
# -----------------------------
bot = Client(
    "BassBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# -----------------------------
# Create assistant client
# -----------------------------
assistant = Client(
    name="assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

pytgcalls = PyTgCalls(assistant)
active_sessions = {}  # chat_id -> file_path

# ==============================
# 🔊 Bass Boost Function
# ==============================
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

# ==============================
# 🎧 Play Audio in VC
# ==============================
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
            AudioPiped(boosted_file),
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

# ==============================
# 🚀 Bot Commands
# ==============================
@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("🎵 BassBot is alive and ready to play your tracks with EXTREME bass!")

# Command to play audio
@bot.on_message(filters.command("bass"))
async def bass_cmd(_, message):
    await message.reply_text("Send me an audio file or voice note to play in VC:")

    # Wait for the next audio/voice message from the same user
    audio_msg = await bot.listen(message.chat.id, filters.audio | filters.voice)
    file_path = await audio_msg.download()
    
    await message.reply_text("Send the target group ID where you want the audio to play:")
    group_msg = await bot.listen(message.chat.id, filters.text)
    chat_id = int(group_msg.text)

    await play_bass(file_path, chat_id)
    await message.reply_text("✅ Playing with EXTREME bass! Use /bstop to stop.")

# Command to stop audio
@bot.on_message(filters.command("bstop"))
async def bstop_cmd(_, message):
    await stop_bass(message.chat.id)
    await message.reply_text("⏹ Stopped the bass playback.")

# ==============================
# Run assistant + bot
# ==============================
async def main():
    await assistant.start()
    await pytgcalls.start()
    await bot.start()
    print("[BassBot] Running with EXTREME bass!")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
