from telethon import events, Button
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import PeerChannel, PeerUser
from telethon.errors import ChatAdminRequiredError
from collections import defaultdict
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, OWNER_ID, SUPPORT_ID, LOGGER_ID, SUDO_USERS
from config import BOT
from src.status import *
import time
import re
import html
import logging
from functools import wraps
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import PeerUser, ChannelParticipantAdmin, ChannelParticipantCreator
from datetime import datetime, timedelta
import asyncio


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


mongo_BOT = MongoClient(MONGO_URI)
db = mongo_BOT[DB_NAME]
users_collection = db['users']
active_groups_collection = db['active_groups']
authorized_users_collection = db['authorized_users']
group_settings_collection = db['group_settings']

message_cache = {}

deletion_tasks = {}

DEFAULT_EDIT_DELAY_MINUTES = 1
MIN_EDIT_DELAY_MINUTES = 1
MAX_EDIT_DELAY_MINUTES = 5


@BOT.on(events.NewMessage(func=lambda e: e.is_group))
async def track_groups(event):
    chat = await event.get_chat()
    group_id = chat.id
    group_name = chat.title or "Unknown Group"
    

    try:
        invite = await BOT(ExportChatInviteRequest(group_id))
        invite_link = f"https://t.me/{invite.link.split('/')[-1]}"
    except ChatAdminRequiredError:
        invite_link = "ɴᴏ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴀᴠᴀɪʟᴀʙʟᴇ"
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɢᴇᴛᴛɪɴɢ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ꜰᴏʀ {group_name}: {e}")
        invite_link = "ɴᴏ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴀᴠᴀɪʟᴀʙʟᴇ"
    

    active_groups_collection.update_one(
        {"group_id": group_id},
        {"$set": {
            "group_name": group_name,
            "invite_link": invite_link
        }},
        upsert=True
    )


@BOT.on(events.NewMessage)
async def cache_message(event):
    if event.message and event.message.text:
        message_cache[(event.chat_id, event.id)] = {
            "text": event.message.text,
            "timestamp": datetime.now().timestamp()
        }


async def delete_message_after_delay(chat_id, message_id, delay_minutes, user_mention, chat_title):
    delay_seconds = delay_minutes * 60
    logger.info(f"ꜱᴄʜᴇᴅᴜʟᴇᴅ ᴅᴇʟᴇᴛɪᴏɴ ꜰᴏʀ ᴍᴇꜱꜱᴀɢᴇ {message_id} ɪɴ ᴄʜᴀᴛ {chat_id} ᴀꜰᴛᴇʀ {delay_minutes} ᴍɪɴᴜᴛᴇꜱ")
    
    try:
        await asyncio.sleep(delay_seconds)
        
        try:
            await BOT.delete_messages(chat_id, message_id)
            logger.info(f"ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ {message_id} ɪɴ ᴄʜᴀᴛ {chat_id} ᴀꜰᴛᴇʀ {delay_minutes} ᴍɪɴᴜᴛᴇꜱ.")
            
    
            await BOT.send_message(
                chat_id,
                f"<blockquote><b>{user_mention}'ꜱ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ {delay_minutes} ᴍɪɴᴜᴛᴇ(ꜱ).</b></blockquote>",
                parse_mode='html',
                buttons=[[Button.url("ᴜᴘᴅᴀᴛᴇꜱ", f"https://t.me/STORM_TECHH")]]
            )
            

            await BOT.send_message(
                LOGGER_ID,
                f"<blockquote><b>ᴅᴇʟᴇᴛᴇᴅ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ {user_mention}\nɪɴ ᴄʜᴀᴛ {chat_title or chat_id} ᴀꜰᴛᴇʀ {delay_minutes} ᴍɪɴᴜᴛᴇ(ꜱ).</b></blockquote>",
                parse_mode='html'
            )
        except Exception as e:
            logger.error(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇ {message_id} ɪɴ ᴄʜᴀᴛ {chat_id}: {e}")
            await BOT.send_message(
                LOGGER_ID,
                f"<blockquote><b>⚠️ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ.\nᴄʜᴀᴛ: {chat_title or chat_id}\nᴍᴇꜱꜱᴀɢᴇ ɪᴅ:: {message_id}\nᴇʀʀᴏʀ: {e}</b></blockquote>",
                parse_mode='html'
            )
    except asyncio.CancelledError:
        logger.info(f"ᴅᴇʟᴇᴛɪᴏɴ ᴛᴀꜱᴋ ꜰᴏʀ ᴍᴇꜱꜱᴀɢᴇ {message_id} ɪɴ ᴄʜᴀᴛ {chat_id} ᴡᴀꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ")
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ ᴅᴇʟᴇᴛᴇ_ᴍᴇꜱꜱᴀɢᴇ_ᴀꜰᴛᴇʀ_ᴅᴇʟᴀʏ ꜰᴏʀ ᴍᴇꜱꜱᴀɢᴇ {message_id} ɪɴ ᴄʜᴀᴛ {chat_id}: {e}")
        await BOT.send_message(
            LOGGER_ID,
            f"<blockquote><b>⚠️ ᴇʀʀᴏʀ ɪɴ ᴅᴇʟᴇᴛᴇ_ᴍᴇꜱꜱᴀɢᴇ_ᴀꜰᴛᴇʀ_ᴅᴇʟᴀʏ.\nᴄʜᴀᴛ: {chat_title or chat_id}\nᴍᴇꜱꜱᴀɢᴇ ɪᴅ: {message_id}\nᴇʀʀᴏʀ: {e}</b></blockquote>",
            parse_mode='html'
        )
    finally:

        if (chat_id, message_id) in deletion_tasks:
            del deletion_tasks[(chat_id, message_id)]


@BOT.on(events.MessageEdited)
async def check_edit(event):
    try:
        chat = await event.get_chat()
        user = await event.get_sender()
        
        if not event.message or not event.message.edit_date:
            return
        
        logger.info(f"ᴍᴇꜱꜱᴀɢᴇ ᴇᴅɪᴛᴇᴅ ɪɴ ᴄʜᴀᴛ {chat.id}, ᴍᴇꜱꜱᴀɢᴇ ɪᴅ: {event.id}")
        
        cached_msg = message_cache.get((event.chat_id, event.id))
        if not cached_msg:
            logger.info(f"ɴᴏ ᴄᴀᴄʜᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰᴏᴜɴᴅ ꜰᴏʀ {event.id} ɪɴ ᴄʜᴀᴛ {chat.id}")
            return
            
        old_text = cached_msg.get("text")
        new_text = event.message.text
        if old_text is not None and old_text == new_text:
            logger.info(f"ᴍᴇꜱꜱᴀɢᴇ ᴛᴇxᴛ ᴜɴᴄʜᴀɴɢᴇᴅ ꜰᴏʀ{event.id} ɪɴ ᴄʜᴀᴛ {chat.id}")
            return
        

        message_cache[(event.chat_id, event.id)] = {
            "text": new_text,
            "timestamp": datetime.now().timestamp()
        }
        

        is_channel_msg = getattr(event.message, "post_author", None) is not None or getattr(event.message, "sender_id", None) is None
        if is_channel_msg:
            await event.delete()
            await BOT.send_message(
                chat.id,
                f"<blockquote><b>ᴀ ᴍᴇꜱꜱᴀɢᴇ ꜱᴇɴᴛ ᴠɪᴀ ᴄʜᴀɴɴᴇʟ ᴏʀ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴡᴀꜱ ᴇᴅɪᴛᴇᴅ.\nɪᴛ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ.</b></blockquote>",
                parse_mode='html',
                buttons=[[Button.url("ᴜᴘᴅᴀᴛᴇꜱ", f"https://t.me/STORM_TECHH")]]
            )
            await BOT.send_message(
                LOGGER_ID,
                f"<blockquote><b>ᴅᴇʟᴇᴛᴇᴅ ᴀɴ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ꜱᴇɴᴛ ᴠɪᴀ ᴄʜᴀɴɴᴇʟ ɪɴ {chat.title or chat.id}.</b></blockquote>",
                parse_mode='html'
            )
            return
        
        if user is None:
            await BOT.send_message(
                LOGGER_ID,
                f"<blockquote><b>⚠️ ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴛʜᴇ ꜱᴇɴᴅᴇʀ ᴏꜰ ᴛʜᴇ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ.\nᴄʜᴀᴛ: {chat.title or chat.id}\nᴍᴇꜱꜱᴀɢᴇ ɪᴅ: {event.id}</b></blockquote>",
                parse_mode='html'
            )
            return
        
        user_id = user.id
        user_first_name = html.escape(user.first_name)
        user_mention = f"<a href='tg://user?id={user_id}'>{user_first_name}</a>"
        
        is_owner = user_id == OWNER_ID
        is_authorized = authorized_users_collection.find_one({"user_id": user_id, "group_id": chat.id})
        
        if is_owner or is_authorized:
            logger.info(f"ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜꜱᴇʀ {user_id} ᴇᴅɪᴛᴇᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ɪɴ {chat.id}. ɴᴏ ᴀᴄᴛɪᴏɴ ᴛᴀᴋᴇɴ.")
            await BOT.send_message(
                LOGGER_ID,
                f"<blockquote><b>ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜꜱᴇʀ {user_mention} ᴇᴅɪᴛᴇᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ɪɴ {chat.title or chat.id}.\nɴᴏ ᴀᴄᴛɪᴏɴ ᴡᴀꜱ ᴛᴀᴋᴇɴ.</b></blockquote>",
                parse_mode='html'
            )
            return
        
        try:
            chat_member = await BOT.get_permissions(chat, user)
            if chat_member.is_admin or chat_member.is_creator:
                user_role = "admin" if chat_member.is_admin else "creator"
                logger.info(f"ᴜꜱᴇʀ {user_id} ɪꜱ ᴀɴ {user_role} ɪɴ ᴄʜᴀᴛ {chat.id}. ɴᴏ ᴀᴄᴛɪᴏɴ ᴛᴀᴋᴇɴ.")
                await BOT.send_message(
                    LOGGER_ID,
                    f"<blockquote><b>ᴜꜱᴇʀ {user_mention} ɪꜱ ᴀɴ {user_role} ɪɴ ᴄʜᴀᴛ {chat.title or chat.id}.\nɴᴏ ᴅᴇʟᴇᴛɪᴏɴ ᴡᴀꜱ ᴘᴇʀꜰᴏʀᴍᴇᴅ.</b></blockquote>",
                    parse_mode='html'
                )
                return
        except Exception as e:
            logger.error(f"ᴇʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ ᴀᴅᴍɪɴ ꜱᴛᴀᴛᴜꜱ ꜰᴏʀ ᴜꜱᴇʀ {user_id} ɪɴ ᴄʜᴀᴛ  {chat.id}: {e}")
            await BOT.send_message(
                LOGGER_ID,
                f"<blockquote><b>⚠️ ʙᴏᴛ ɴᴇᴇᴅꜱ ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ ᴛᴏ ᴄʜᴇᴄᴋ ᴇᴅɪᴛꜱ\nᴄʜᴀᴛ: {chat.title or chat.id}\nError: {e}</b></blockquote>",
                parse_mode='html'
            )
            return
        
        group_settings = group_settings_collection.find_one({"group_id": chat.id})
        edit_delay_minutes = group_settings.get("edit_delay_minutes", DEFAULT_EDIT_DELAY_MINUTES) if group_settings else DEFAULT_EDIT_DELAY_MINUTES
        
        if edit_delay_minutes > 0:
            logger.info(f"ᴇᴅɪᴛ ᴅᴇʟᴀʏ ɪꜱ ꜱᴇᴛ ᴛᴏ {edit_delay_minutes} ᴍɪɴᴜᴛᴇꜱ ꜰᴏʀ ᴄʜᴀᴛ {chat.id}")
            
            if (event.chat_id, event.id) in deletion_tasks:
                logger.info(f"ᴄᴀɴᴄᴇʟʟɪɴɢ ᴇxɪꜱᴛɪɴɢ ᴅᴇʟᴇᴛɪᴏɴ ᴛᴀꜱᴋ ꜰᴏʀ ᴍᴇꜱꜱᴀɢᴇ {event.id} ɪɴ ᴄʜᴀᴛ {chat.id}")
                deletion_tasks[(event.chat_id, event.id)].cancel()
        
            await BOT.send_message(
                chat.id,
                f"<blockquote><b>{user_mention}'s ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ {edit_delay_minutes} ᴍɪɴᴜᴛᴇ(ꜱ).</b></blockquote>",
                parse_mode='html'
            )
            
            task = asyncio.create_task(
                delete_message_after_delay(
                    chat.id, 
                    event.id, 
                    edit_delay_minutes, 
                    user_mention, 
                    chat.title or chat.id
                )
            )
            deletion_tasks[(event.chat_id, event.id)] = task
            logger.info(f"ᴄʀᴇᴀᴛᴇᴅ ᴅᴇʟᴇᴛɪᴏɴ ᴛᴀꜱᴋ ꜰᴏʀ ᴍᴇꜱꜱᴀɢᴇ {event.id} ɪɴ ᴄʜᴀᴛ {chat.id}")
            
    except Exception as e:
        logger.error(f"ᴜɴʜᴀɴᴅʟᴇᴅ ᴇxᴄᴇᴘᴛɪᴏɴ ɪɴ ᴄʜᴇᴄᴋ_ᴇᴅɪᴛ: {e}")
        await BOT.send_message(
            LOGGER_ID,
            f"<blockquote><b>⚠️ ᴜɴʜᴀɴᴅʟᴇᴅ ᴇxᴄᴇᴘᴛɪᴏɴ\nᴇʀʀᴏʀ: {e}</b></blockquote>",
            parse_mode='html'
        )


def is_admin(func):
    @wraps(func)
    async def wrapper(event):
        user = await event.get_sender()
        chat = await event.get_chat()
        if user.id == OWNER_ID:
            return await func(event)
        try:
            participant = await BOT(GetParticipantRequest(chat, user))
            if isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                return await func(event)
            else:
                return await event.reply(f"<blockquote>🚫 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ, ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ꜰɪʀꜱᴛ</blockquote>", parse_mode='html')
        except Exception as e:
            return await event.reply(f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴅᴍɪɴ ꜱᴛᴀᴛᴜꜱ: {e}</blockquote>", parse_mode='html')
    return wrapper


@BOT.on(events.NewMessage(pattern='/edelay(?: |$)(.*)'))
@is_admin
async def set_edit_delay(event):
    chat = await event.get_chat()
    delay_str = event.pattern_match.group(1).strip()
    
    if not delay_str:
        group_settings = group_settings_collection.find_one({"group_id": chat.id})
        current_delay_minutes = group_settings.get("edit_delay_minutes", DEFAULT_EDIT_DELAY_MINUTES) if group_settings else DEFAULT_EDIT_DELAY_MINUTES
        await event.reply(
            f"<blockquote>ᴄᴜʀʀᴇɴᴛ ᴇᴅɪᴛ ᴅᴇʟᴀʏ: {current_delay_minutes} ᴍɪɴᴜᴛᴇ(ꜱ)\n"
            f"ᴍᴇꜱꜱᴀɢᴇꜱ ᴛʜᴀᴛ ᴀʀᴇ ᴇᴅɪᴛᴇᴅ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ ᴛʜɪꜱ ᴛɪᴍᴇ.\n"
            f"ᴜꜱᴀɢᴇ: /edelay <ᴍɪɴᴜᴛᴇꜱ> (0 ᴛᴏ ᴅɪꜱᴀʙʟᴇ, ᴍɪɴ: {MIN_EDIT_DELAY_MINUTES}, ᴍᴀx: {MAX_EDIT_DELAY_MINUTES})</blockquote>", 
            parse_mode='html'
        )
        return
    
    try:
        delay_minutes = int(delay_str)
        
        if delay_minutes < 0:
            await event.reply(f"<blockquote>❌ ᴅᴇʟᴀʏ ᴄᴀɴ'ᴛ ʙᴇ ɴᴇɢᴀᴛɪᴠᴇ. ᴜꜱᴇ 0 ᴛᴏ ᴅɪꜱᴀʙʟᴇ.</blockquote>", parse_mode='html')
            return
        elif delay_minutes > 0 and delay_minutes < MIN_EDIT_DELAY_MINUTES:
            await event.reply(
                f"<blockquote>❌ ᴍɪɴɪᴍᴜᴍ ᴅᴇʟᴀʏ ɪꜱ {MIN_EDIT_DELAY_MINUTES} ᴍɪɴᴜᴛᴇ(ꜱ). ꜱᴇᴛᴛɪɴɢ ᴛᴏ {MIN_EDIT_DELAY_MINUTES} ᴍɪɴᴜᴛᴇ(ꜱ).</blockquote>", 
                parse_mode='html'
            )
            delay_minutes = MIN_EDIT_DELAY_MINUTES
        elif delay_minutes > MAX_EDIT_DELAY_MINUTES:
            await event.reply(
                f"<blockquote>❌ ᴍɪɴɪᴍᴜᴍ ᴅᴇʟᴀʏ ɪꜱ {MAX_EDIT_DELAY_MINUTES} ᴍɪɴᴜᴛᴇ(ꜱ). ꜱᴇᴛᴛɪɴɢ ᴛᴏ {MAX_EDIT_DELAY_MINUTES} ᴍɪɴᴜᴛᴇ(ꜱ).</blockquote>", 
                parse_mode='html'
            )
            delay_minutes = MAX_EDIT_DELAY_MINUTES
            
        group_settings_collection.update_one(
            {"group_id": chat.id},
            {"$set": {"edit_delay_minutes": delay_minutes}},
            upsert=True
        )
        
        if delay_minutes == 0:
            await event.reply(
                f"<blockquote>✅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛɪᴏɴ ᴏꜰ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ʜᴀꜱ ʙᴇᴇɴ <b>ᴅɪꜱᴀʙʟᴇᴅ</b> ɪɴ ᴛʜɪꜱ ᴄʜᴀᴛ.</blockquote>", 
                parse_mode='html'
            )
        else:
            await event.reply(
                f"<blockquote>✅ ᴛʜᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛɪᴏɴ ᴏꜰ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇᴛ ᴛᴏ <b>{delay_minutes} ᴍɪɴᴜᴛᴇ(ꜱ)</b> ɪɴ ᴛʜɪꜱ ᴄʜᴀᴛ.\n"
                f"ᴡʜᴇɴ ᴀ ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ᴇᴅɪᴛᴇᴅ, ɪᴛ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ {delay_minutes} ᴍɪɴᴜᴛᴇ(ꜱ).</blockquote>", 
                parse_mode='html'
            )
        
        logger.info(f"ᴇᴅɪᴛ ᴅᴇʟᴀʏ ꜱᴇᴛ ᴛᴏ {delay_minutes} ᴍɪɴᴜᴛᴇꜱ ꜰᴏʀ ᴄʜᴀᴛ{chat.id}")
    except ValueError:
        await event.reply(
            f"<blockquote>❌ ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ᴏꜰ ᴍɪɴᴜᴛᴇꜱ.\n"
            f"ᴇxᴀᴍᴘʟᴇ: /edelay 2 (ꜰᴏʀ 2 ᴍɪɴᴜᴛᴇꜱ)\n"
            f"/edelay 0 ᴛᴏ ᴅɪꜱᴀʙʟᴇ\n"
            f"ᴍɪɴ: {MIN_EDIT_DELAY_MINUTES}, ᴍᴀx: {MAX_EDIT_DELAY_MINUTES}</blockquote>", 
            parse_mode='html'
        )
    except Exception as e:
        await event.reply(f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇᴛ ᴇᴅɪᴛ ᴅᴇʟᴀʏ: {e}</blockquote>", parse_mode='html')
        logger.error(f"ᴇʀʀᴏʀ ꜱᴇᴛᴛɪɴɢ ᴇᴅɪᴛ ᴅᴇʟᴀʏ ꜰᴏʀ ɢʀᴏᴜᴘ {chat.id}: {e}")


@BOT.on(events.NewMessage(pattern='/auth(?: |$)(.*)'))
@is_admin
async def auth(event):
    user = await event.get_sender()
    chat = await event.get_chat()
    sudo_user = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else None
    
    if not sudo_user and not event.is_reply:
        await event.reply(f"<blockquote>ᴜꜱᴀɢᴇ: /auth <ᴜꜱᴇʀɴᴀᴍᴇ/ᴜꜱᴇʀ_ɪᴅ> ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ʜɪꜱ/ʜᴇʀ ᴍᴇꜱꜱᴀɢᴇ.</blockquote>", parse_mode='html')
        return
    
    try:
        if not sudo_user and event.is_reply:
            reply = await event.get_reply_message()
            user_entity = await reply.get_sender()
            if not user_entity:
                await event.reply(f"<blockquote>❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇᴛʀɪᴇᴠᴇ ᴜꜱᴇʀ ꜰʀᴏᴍ ʀᴇᴘʟʏ.</blockquote>", parse_mode='html')
                return
            sudo_user_id = user_entity.id
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))
        elif sudo_user.startswith('@'):
            user_entity = await BOT.get_entity(sudo_user)
            sudo_user_id = user_entity.id
        else:
            sudo_user_id = int(sudo_user)
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))
        
        if authorized_users_collection.find_one({"user_id": sudo_user_id, "group_id": chat.id}):
            await event.reply(f"<blockquote>{user_entity.first_name} ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</blockquote>", parse_mode='html')
            return
        
        authorized_users_collection.insert_one({
            "user_id": sudo_user_id,
            "username": getattr(user_entity, 'username', None),
            "first_name": getattr(user_entity, 'first_name', 'Unknown'),
            "group_id": chat.id,
            "authorized_by": user.id,
            "authorized_at": datetime.now()
        })
        
        await event.reply(
            f"<blockquote>✅ {user_entity.first_name} ʜᴀꜱ ʙᴇᴇɴ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.\n"
            f"ᴛʜᴇʏ ᴄᴀɴ ɴᴏᴡ ᴇᴅɪᴛ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇᴍ ʙᴇɪɴɢ ᴅᴇʟᴇᴛᴇᴅ.</blockquote>", 
            parse_mode='html'
        )
    except Exception as e:
        await event.reply(f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴜᴛʜᴏʀɪᴢᴇ ᴜꜱᴇʀ: {e}</blockquote>", parse_mode='html')
        logger.error(f"ᴇʀʀᴏʀ ᴀᴜᴛʜᴏʀɪᴢɪɴɢ ᴜꜱᴇʀ ɪɴ ɢʀᴏᴜᴘ {chat.id}: {e}")


@BOT.on(events.NewMessage(pattern='/unauth(?: |$)(.*)'))
@is_admin
async def unauth(event):
    user = await event.get_sender()
    chat = await event.get_chat()
    sudo_user = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else None
    
    if not sudo_user and not event.is_reply:
        await event.reply(f"<blockquote>ᴜꜱᴀɢᴇ: /unauth <ᴜꜱᴇʀɴᴀᴍᴇ/ᴜꜱᴇʀ_ɪᴅ> ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ʜɪꜱ/ʜᴇʀ ᴍᴇꜱꜱᴀɢᴇ.</blockquote>", parse_mode='html')
        return
    
    try:
        if not sudo_user and event.is_reply:
            reply = await event.get_reply_message()
            user_entity = await reply.get_sender()
            if not user_entity:
                await event.reply(f"<blockquote>❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇᴛʀɪᴇᴠᴇ ᴜꜱᴇʀ ꜰʀᴏᴍ ʀᴇᴘʟʏ.</blockquote>", parse_mode='html')
                return
            sudo_user_id = user_entity.id
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))
        elif sudo_user.startswith('@'):
            user_entity = await BOT.get_entity(sudo_user)
            sudo_user_id = user_entity.id
        else:
            sudo_user_id = int(sudo_user)
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))
        
        if not authorized_users_collection.find_one({"user_id": sudo_user_id, "group_id": chat.id}):
            await event.reply(f"<blockquote>{user_entity.first_name} ɪꜱ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</blockquote>", parse_mode='html')
            return
        
        authorized_users_collection.delete_one({"user_id": sudo_user_id, "group_id": chat.id})
        await event.reply(
            f"<blockquote>✅ {user_entity.first_name} ʜᴀꜱ ʙᴇᴇɴ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.\n"
            f"ᴛʜᴇɪʀ ᴇᴅɪᴛᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡɪʟʟ ɴᴏᴡ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ'ꜱ ᴇᴅɪᴛ ᴅᴇʟᴀʏ ꜱᴇᴛᴛɪɴɢꜱ.</blockquote>", 
            parse_mode='html'
        )
    except Exception as e:
        await event.reply(f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ ᴜꜱᴇʀ: {e}</blockquote>", parse_mode='html')
        logger.error(f"ᴇʀʀᴏʀ ᴜɴᴀᴜᴛʜᴏʀɪᴢɪɴɢ ᴜꜱᴇʀ ɪɴ ɢʀᴏᴜᴘ {chat.id}: {e}")


@BOT.on(events.NewMessage(pattern='/authlist'))
@is_admin
async def authlist(event):
    chat = await event.get_chat()
    try:
        
        authorized_users = list(authorized_users_collection.find({"group_id": chat.id}))
        
        if not authorized_users:
            await event.reply(f"<blockquote>ɴᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜꜱᴇʀꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.</blockquote>", parse_mode='html')
            return
        
        response = ["🛡️ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜꜱᴇʀꜱ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ:\n"]
        for user in authorized_users:
            user_info = f"\n• {user.get('first_name', 'Unknown')} (ID: {user['user_id']})"
            if user.get('username'):
                user_info += f" (@{user['username']})"
            
    
            if user.get('authorized_by'):
                try:
                    auth_by = await BOT.get_entity(PeerUser(user['authorized_by']))
                    auth_by_name = getattr(auth_by, 'first_name', 'Unknown')
                    user_info += f"\n  ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ʙʏ: {auth_by_name}"
                except:
                    user_info += f"\n  ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ʙʏ: ɪᴅ {user['authorized_by']}"
            
            if user.get('authorized_at'):
                auth_time = user['authorized_at'].strftime('%Y-%m-%d %H:%M:%S')
                user_info += f"\n  At: {auth_time}"
            
            response.append(user_info)
        
        response.append("</blockquote>")
        await event.reply("".join(response), parse_mode='html')
    except Exception as e:
        await event.reply(f"<blockquote>❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜꜱᴇʀꜱ: {e}</blockquote>", parse_mode='html')
        logger.error(f"ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜꜱᴇʀꜱ ꜰᴏʀ ɢʀᴏᴜᴘ {chat.id}: {e}")

# Send bot statistics
@BOT.on(events.NewMessage(pattern='/stats'))
async def send_stats(event):
    user = await event.get_sender()

    if user.id != OWNER_ID:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ  ᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    try:
        users_count = users_collection.count_documents({})
        chat_count = active_groups_collection.count_documents({})  # Use correct collection

        stats_msg = f"Tᴏᴛᴀʟ Usᴇʀs: {users_count}\nTᴏᴛᴀʟ Gʀᴏᴜᴘs: {chat_count}\n"
        await event.reply(stats_msg)
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ send_stats ғᴜɴᴄᴛɪᴏɴ: {e}")
        await event.reply("Fᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ sᴛᴀs.")

# List active groups
@BOT.on(events.NewMessage(pattern='/activegroups'))
async def list_active_groups(event):
    user = await event.get_sender()

    if user.id != OWNER_ID:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    active_groups_from_db = fetch_active_groups_from_db()

    if not active_groups_from_db:
        await event.reply("Tʜᴇ ᴇɢ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ ɪɴ ᴀɴʏ ɢʀᴏᴜᴘs ᴏʀ ғᴀɪʟᴇᴅ ᴛᴏ ᴄᴏᴍɴᴇᴄᴛ ᴛᴏ MᴏɴɢᴏDB.")
        return

    group_list_msg = "Aᴄᴛɪᴠᴇ ɢʀᴏᴜᴘs:\n"
    for group in active_groups_from_db:
        group_name = group.get("group_name", "Unknown Group")
        invite_link = group.get("invite_link", "Nᴏ ɪɴᴠɪᴛᴀᴛɪᴏɴ ᴀᴠᴀɪʟᴀʙʟᴅ")

        if invite_link != "ɪɴᴠɪᴛᴀᴛᴀᴛɪᴏɴ ᴀᴠᴀɪʟᴀʙʟᴇ":
            group_list_msg += f"- <a href='{invite_link}'>[{group_name}]</a>\n"
        else:
            group_list_msg += f"- {group_name}\n"

    await event.reply(group_list_msg, parse_mode='html')

# Fetch active groups from MongoDB
def fetch_active_groups_from_db():
    try:
        active_groups = list(active_groups_collection.find({}, {"group_id": 1, "group_name": 1, "invite_link": 1, "_id": 0}))
        return active_groups
    except Exception as e:
        print(f"Fᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ MᴏɴɢᴏDB: {e}")
        return None
