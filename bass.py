# bass.py

from pyrogram import filters
from pyrogram.types import Message
from main import bot
from assistant import play_bass, stop_bass

user_audio = {}
user_target = {}

@bot.on_message(filters.command("bass") & filters.private)
async def bass_start(client, message: Message):
    await message.reply_text("🎵 Send me the audio file or voice note you want to play in the group VC.")

@bot.on_message(filters.audio | filters.voice & filters.private)
async def receive_audio(client, message: Message):
    user_id = message.from_user.id
    file = await message.download()
    user_audio[user_id] = file
    await message.reply_text("✅ Got the audio! Now send me the Telegram group ID where you want it to play:")

@bot.on_message(filters.text & filters.private)
async def receive_group_id(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_audio:
        return
    try:
        chat_id = int(message.text)
        user_target[user_id] = chat_id
        await message.reply_text(f"✅ Starting playback in group `{chat_id}`...")
        await play_bass(user_audio[user_id], chat_id)
    except ValueError:
        await message.reply_text("❌ Invalid group ID. Send only numbers.")

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
