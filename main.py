import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from py_tgcalls import PyTgCalls, idle, AudioPiped
import ffmpeg
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# -------------------------
# Pyrogram Bot Client
# -------------------------
bot = Client(
    "BassBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# -------------------------
# Assistant Client
# -------------------------
assistant = Client(
    name="assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

pytgcalls = PyTgCalls(assistant)

# -------------------------
# Active playback sessions
# -------------------------
active_sessions = {}  # chat_id -> boosted_file_path

# -------------------------
# Bass Boost Function
# -------------------------
def apply_bass_boost(input_file: str) -> str:
    boosted_file = f"boosted_{os.path.basename(input_file)}"
    try:
        (
            ffmpeg
            .input(input_file)
            .output(
                boosted_file,
                af="bass=g=25:f=80,volume=10dB",
                format="wav",
                acodec="pcm_s16le",
                ac=2,
                ar="44100"
            )
            .overwrite_output()
            .run(quiet=True)
        )
        return boosted_file
    except Exception as e:
        print(f"[BassFilterError] {e}")
        return input_file

# -------------------------
# Play Audio / Voice in VC
# -------------------------
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

# -------------------------
# Command Handlers
# -------------------------
# Alive /start
@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply(
        "🎧 **BassBot is alive!**\n"
        "Send /bass to play audio with extreme loud bass.\n"
        "Send /bstop to stop playback."
    )

# /bass command
user_state = {}  # track what user is doing: {"waiting_audio": True, "waiting_chat_id": True, ...}

@bot.on_message(filters.command("bass"))
async def bass_handler(client, message: Message):
    user_id = message.from_user.id
    user_state[user_id] = {"waiting_audio": True}
    await message.reply("Send me the audio file or voice note you want to play with extreme bass:")

@bot.on_message(filters.audio | filters.voice)
async def audio_handler(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_state or not user_state[user_id].get("waiting_audio"):
        return  # ignore if user didn't trigger /bass

    file_path = await message.download()
    user_state[user_id]["file_path"] = file_path
    user_state[user_id]["waiting_audio"] = False
    user_state[user_id]["waiting_chat_id"] = True

    await message.reply("Got the audio! Now send the Telegram group ID where I should play it:")

@bot.on_message(filters.text)
async def chatid_handler(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_state:
        return
    state = user_state[user_id]
    if state.get("waiting_chat_id"):
        try:
            chat_id = int(message.text.strip())
        except:
            await message.reply("Please send a valid numeric Telegram group ID.")
            return
        state["waiting_chat_id"] = False
        file_path = state["file_path"]

        # Start assistant + PyTgCalls if not running
        if not pytgcalls.is_connected:
            await assistant.start()
            await pytgcalls.start()

        await play_bass(file_path, chat_id)
        await message.reply(f"✅ Started playing your audio in chat `{chat_id}` with extreme bass!")
        user_state.pop(user_id)

# /bstop command
@bot.on_message(filters.command("bstop"))
async def stop_handler(client, message: Message):
    chat_id = message.chat.id
    await stop_bass(chat_id)
    await message.reply("🛑 Playback stopped.")

# -------------------------
# Run Bot + Assistant
# -------------------------
async def main():
    await bot.start()
    print("[BassBot] Running...")
    await idle()  # keeps pytgcalls running
    await bot.idle()

if __name__ == "__main__":
    asyncio.run(main())
