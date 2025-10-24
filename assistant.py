from pyrogram import Client
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
import asyncio
from config import API_ID, API_HASH, SESSION_STRING

# Create Assistant Client
assistant = Client(
    name="assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

pytgcalls = PyTgCalls(assistant)

# Keep track of active loops
active_sessions = {}

async def play_bass(file_path: str, chat_id: int):
    """Play or restart bass audio in VC loop."""
    try:
        await assistant.join_chat(chat_id)
    except Exception:
        pass  # already joined or no permission

    active_sessions[chat_id] = file_path

    try:
        await pytgcalls.join_group_call(
            chat_id,
            AudioPiped(file_path),
        )
    except Exception as e:
        print(f"[BassError] {e}")

@pytgcalls.on_stream_end()
async def restart_stream(_, update):
    """When track ends, replay automatically (loop)."""
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
        del active_sessions[chat_id]

async def run_assistant():
    """Run the assistant client + PyTgCalls."""
    await assistant.start()
    await pytgcalls.start()
    print("[Assistant] Running...")
    await idle()
