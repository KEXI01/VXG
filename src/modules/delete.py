from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import asyncio
from config import BOT
from src.status import *


delay_times = {}


@BOT.on(events.NewMessage(pattern='/setdelay'))
@is_admin
async def set_delay(event, _s=None):  # Add _s as an optional argument
    try:
        # Extract the delay time from the command
        delay = int(event.message.text.split(' ')[1])
        if delay < 1:
            await event.reply("ᴅᴇʟᴀʏ ᴛɪᴍᴇ ᴍᴜꜱᴛ ʙᴇ ᴀᴛ ʟᴇᴀꜱᴛ 1 ᴍɪɴᴜᴛᴇ.")
            return

        # Save the delay time for the chat
        chat_id = event.chat_id
        delay_times[chat_id] = delay
        await event.reply(f"ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛɪᴏɴ ᴅᴇʟᴀʏ ꜱᴇᴛ ᴛᴏ {delay} ᴍɪɴᴜᴛᴇꜱ.")

    except (IndexError, ValueError):
        await event.reply("ᴜꜱᴀɢᴇ: /setdelay <ᴛɪᴍᴇ_ɪɴ_ᴍɪɴᴜᴛᴇꜱ>")
        
@BOT.on(events.NewMessage(func=lambda e: e.is_group and e.media))
async def handle_media(event):
    chat_id = event.chat_id
    if chat_id in delay_times:
        delay = delay_times[chat_id]
        await asyncio.sleep(delay * 60)

        try:
            await event.delete()
        except Exception:
            pass
