# bass.py

from pyrogram import filters
from pyrogram.types import Message
from main import bot
from assistant import play_bass, stop_bass

# Temporary storage
user_audio = {}   # user_id -> file path
user_target = {}  # user_id -> chat_id

# Step 1: /bass command → ask for audio/voice
@bot.on_message(filters.command("bass") & filters.private)
async def bass_start(client, message: Message):
    await message.reply_text(
        "🎵 Reply to this message with an audio file or voice note you want to play in the group VC."
    )

# Step 2: Handle audio/voice replies
@bot.on_message(filters.audio | filters.voice & filters.private)
async def receive_audio(client, message: Message):
    if not message.reply_to_message:
        return  # ensure the user is replying to /bass
    user_id = message.from_user.id
    file_path = await message.download()  # download audio/voice
    user_audio[user_id] = file_path
    await message.reply_text("✅ Got the audio! Now send me the Telegram group ID where you want it to play:")

# Step 3: Receive group ID
@bot.on_message(filters.text & filters.private)
async def receive_group_id(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_audio:
        return  # user did not send audio yet
    try:
        chat_id = int(message.text)
        user_target[user_id] = chat_id
        await message.reply_text(f"✅ Starting playback in group `{chat_id}`...")
        await play_bass(user_audio[user_id], chat_id)
    except ValueError:
        await message.reply_text("❌ Invalid group ID. Send only numbers.")

# Step 4: Stop playback
@bot.on_message(filters.command("bstop") & filters.private)
async def stop(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_target:
        chat_id = user_target[user_id]
        await stop_bass(chat_id)
        await message.reply_text("⏹ Stopped playback.")
        user_audio.pop(user_id, None)
        user_target.pop(user_id, None)
    else:
        await message.reply_text("❌ No active playback found.")
