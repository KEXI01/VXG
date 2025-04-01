from typing import Dict, Union
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins
from config import BOT
from src.status import *
MONGO_DB_URI = "mongodb+srv://kunaalkumar0091:6qhyyQIyS2idoGFQ@cluster0.z2jge.mongodb.net/?retryWrites=true&w=majority"

mongo = MongoCli(MONGO_DB_URI).Rankings
impdb = mongo.pretender

async def usr_data(chat_id: int, user_id: int) -> bool:
    user = await impdb.find_one({"chat_id": chat_id, "user_id": user_id})
    return bool(user)

async def get_userdata(chat_id: int, user_id: int) -> Union[Dict[str, str], None]:
    user = await impdb.find_one({"chat_id": chat_id, "user_id": user_id})
    return user

async def add_userdata(chat_id: int, user_id: int, username: str, first_name: str, last_name: str):
    await impdb.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {
            "$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        },
        upsert=True,
    )

async def check_pretender(chat_id: int) -> bool:
    chat = await impdb.find_one({"chat_id_toggle": chat_id})
    return bool(chat)

async def impo_on(chat_id: int) -> None:
    await impdb.insert_one({"chat_id_toggle": chat_id})

async def impo_off(chat_id: int) -> None:
    await impdb.delete_one({"chat_id_toggle": chat_id})

@BOT.on(events.NewMessage(func=lambda e: e.is_group and not e.sender.bot and not e.via_bot_id))
async def chk_usr(event):
    chat_id = event.chat_id
    if event.sender_id is None or not await check_pretender(chat_id):
        return
    user_id = event.sender_id
    user_data = await get_userdata(chat_id, user_id)
    if not user_data:
        await add_userdata(
            chat_id,
            user_id,
            event.sender.username,
            event.sender.first_name,
            event.sender.last_name,
        )
        return

    usernamebefore = user_data.get("username", "")
    first_name = user_data.get("first_name", "")
    lastname_before = user_data.get("last_name", "")

    msg = f"{event.sender_id}\n"

    changes = []

    if (
        first_name != event.sender.first_name
        and lastname_before != event.sender.last_name
    ):
        changes.append(
            f"{first_name} {lastname_before} ʜᴀꜱ ᴄʜᴀɴɢᴇᴅ ᴛʜᴇɪʀ ғʀᴏᴍ {first_name} {lastname_before} ᴛᴏ {event.sender.first_name} {event.sender.last_name}\n"
        )
    elif first_name != event.sender.first_name:
        changes.append(
            f"{first_name} ʜᴀꜱ ᴄʜᴀɴɢᴇᴅ ᴛʜᴇɪʀ ғɪʀsᴛ ɴᴀᴍᴇ ғʀᴏᴍ {first_name} ᴛᴏ {event.sender.first_name}\n"
        )
    elif lastname_before != event.sender.last_name:
        changes.append(
            f"{lastname_before} ʜᴀꜱ ᴄʜᴀɴɢᴇᴅ ᴛʜᴇɪʀ ʟᴀsᴛ ɴᴀᴍᴇ ғʀᴏᴍ {lastname_before} ᴛᴏ {event.sender.last_name}\n"
        )

    if usernamebefore != event.sender.username:
        changes.append(
            f"@{usernamebefore} ʜᴀꜱ ᴄʜᴀɴɢᴇᴅ ᴛʜᴇɪʀ ᴜsᴇʀɴᴀᴍᴇ ғʀᴏᴍ @{usernamebefore} �ᴛᴏ @{event.sender.username}\n"
        )

    if changes:
        msg += "".join(changes)
        await event.reply(msg)

    await add_userdata(
        chat_id,
        user_id,
        event.sender.username,
        event.sender.first_name,
        event.sender.last_name,
    )

@BOT.on(events.NewMessage(pattern=r"/pretender(?: |$)(.*)"))
@is_admin
async def set_mataa(event, _s):  # Accept _s argument
    if event.is_group:
        admin_ids = [user.id async for user in BOT.iter_participants(event.chat_id, filter=ChannelParticipantsAdmins)]
        if event.sender_id not in admin_ids:
            return
        if not event.pattern_match.group(1):
            return await event.reply("ᴅᴇᴛᴇᴄᴛᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴜsᴀɢᴇ:\n/pretender on|off")
        chat_id = event.chat_id
        command = event.pattern_match.group(1).strip()
        if command == "on":
            cekset = await check_pretender(chat_id)
            if cekset:
                await event.reply(f"ᴘʀᴇᴛᴇɴᴅᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ �ᴇɴᴀʙʟᴇᴅ ғᴏʀ {event.chat.title}")
            else:
                await impo_on(chat_id)
                await event.reply(f"sᴜᴄᴇssғᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ғᴏʀ {event.chat.title}")
        elif command == "off":
            cekset = await check_pretender(chat_id)
            if not cekset:
                await event.reply(f"ᴘʀᴇᴛᴇɴᴅᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ {event.chat.title}")
            else:
                await impo_off(chat_id)
                await event.reply(f"sᴜᴄᴇssғᴜʟʟʏ ᴅɪsᴀʙʟᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ғᴏʀ {event.chat.title}")
        else:
            await event.reply("ᴅᴇᴛᴇᴄᴛᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴜsᴀɢᴇ:\n/pretender on|off")
