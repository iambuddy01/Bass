from pyrogram import Client
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
import asyncio
import os
import ffmpeg
from config import API_ID, API_HASH, SESSION_STRING

# Create Assistant Client
assistant = Client(
    name="assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

pytgcalls = PyTgCalls(assistant)

# Active playback sessions
active_sessions = {}

# ==============================
# 🔊 Bass Filter Function
# ==============================
def apply_bass_boost(input_file: str) -> str:
    """
    Applies a heavy bass and volume boost to the input audio.
    Returns the path to the processed temporary file.
    """
    boosted_file = "boosted_" + os.path.basename(input_file)
    try:
        (
            ffmpeg
            .input(input_file)
            # Filters: equalizer for low freq boost + volume increase
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
        return input_file  # fallback to original if filter fails

# ==============================
# 🎧 Player Functions
# ==============================
async def play_bass(file_path: str, chat_id: int):
    """Play or restart bass audio in VC loop."""
    try:
        await assistant.join_chat(chat_id)
    except Exception:
        pass

    # Apply bass boost
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
    """Replay when stream ends (loop)."""
    chat_id = update.chat_id
    if chat_id in active_sessions:
        file = active_sessions[chat_id]
        await asyncio.sleep(2)
        await play_bass(file, chat_id)

async def stop_bass(chat_id: int):
    """Stop playback."""
    try:
        await pytgcalls.leave_group_call(chat_id)
    except Exception:
        pass
    if chat_id in active_sessions:
        file = active_sessions.pop(chat_id)
        try:
            os.remove(file)
        except:
            pass

async def run_assistant():
    """Run the assistant client + PyTgCalls."""
    await assistant.start()
    await pytgcalls.start()
    print("[Assistant] Running with Extreme Bass Boost 🔊")
    await idle()
