from telethon import events, Button
from config import BOT
from src.status import *
import time

@BOT.on(events.NewMessage(pattern=r"/purge"))
@is_admin
async def purge_messages(event, perm):
    if not perm.delete_messages:
         await event.reply("ʏᴏᴜ ᴀʀᴇ ᴍɪꜱꜱɪɴɢ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ:ᴄᴀɴᴅᴇʟᴍꜱɢꜱ!")
         return
    start = time.perf_counter()
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply(
            "Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴇʟᴇᴄᴛ ᴡʜᴇʀᴇ ᴛᴏ ꜱᴛᴀʀᴛ ᴘᴜʀɢɪɴɢ ꜰʀᴏᴍ.")
        return
    messages = []
    message_id = reply_msg.id
    delete_to = event.message.id

    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []

    await event.client.delete_messages(event.chat_id, messages)
    time_ = time.perf_counter() - start
    text = f"ᴘᴜʀɢᴇᴅ ɪɴ {time_:0.2f} Second(s)"
    await event.respond(text, parse_mode='markdown')

@BOT.on(events.NewMessage(pattern="/spurge"))
@is_admin
async def spurge(event, perm):
    if not perm.delete_messages:
         await event.reply("ʏᴏᴜ ᴀʀᴇ ᴍɪꜱꜱɪɴɢ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ:ᴄᴀɴᴅᴇʟᴍꜱɢꜱ!")
         return
    start = time.perf_counter()
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply(
            "ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴇʟᴇᴄᴛ ᴡʜᴇʀᴇ ᴛᴏ ꜱᴛᴀʀᴛ ᴘᴜʀɢɪɴɢ ꜰʀᴏᴍ.")
        return
    messages = []
    message_id = reply_msg.id
    delete_to = event.message.id

    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []

    await event.client.delete_messages(event.chat_id, messages)

@BOT.on(events.NewMessage(pattern="/del$"))
@is_admin
async def delete_messages(event, perm):
    if not perm.delete_messages:
       await event.reply("ʏᴏᴜ ᴀʀᴇ ᴍɪꜱꜱɪɴɢ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ:ᴄᴀɴᴅᴇʟᴍꜱɢꜱ!")
       return
    msg = await event.get_reply_message()
    if not msg:
      await event.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍꜱɢ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɪᴛ.")
      return

    await msg.delete()
    await event.delete()
