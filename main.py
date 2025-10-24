# main.py

import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from assistant import run_assistant
import bass

bot = Client(
    "BassBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="."),
)

async def main():
    await bot.start()
    print("[BassBot] Running...")
    await run_assistant()  # assistant + PyTgCalls
    await bot.idle()

if __name__ == "__main__":
    asyncio.run(main())
