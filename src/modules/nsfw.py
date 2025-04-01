from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import os
import re
import asyncio
import config
from config import BOT

SPOILER = config.SPOILER_MODE
slangf = 'slang_words.txt'

with open(slangf, 'r') as f:
    slang_words = set(line.strip().lower() for line in f)

model_name = "AdamCodd/vit-base-nsfw-detector"
feature_extractor = AutoImageProcessor.from_pretrained(model_name, use_fast=True)
model = AutoModelForImageClassification.from_pretrained(model_name)

def process_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = feature_extractor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            return torch.argmax(logits, dim=-1).item() == 1
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ɪᴍᴀɢᴇ: {e}")
        return False

async def check_nsfw_media(file_path):
    return await asyncio.to_thread(process_image, file_path)

@BOT.on(events.NewMessage(func=lambda e: e.is_group and (e.photo)))
async def media_handler(event):
    try:
        file_path = await event.download_media()
        nsfw = await check_nsfw_media(file_path)
        
        if nsfw:
            name = event.sender.first_name
            await event.delete()
            warning_msg = await event.respond(f"**⚠️ ɴꜱꜰᴡ ᴅᴇᴛᴇᴄᴛᴇᴅ**\n{name}")
            
            if SPOILER:
                spoiler_msg = await event.respond(f"||ʏᴏᴜʀ ᴍᴇᴅɪᴀ ᴡᴀꜱ ʀᴇᴍᴏᴠᴇᴅ !!||")
                await asyncio.sleep(60)
                await spoiler_msg.delete()
            
            await asyncio.sleep(60)
            await warning_msg.delete()

        os.remove(file_path)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ: {e}")

slang_pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in slang_words) + r')\b', re.IGNORECASE)

@BOT.on(events.NewMessage(pattern=None))
async def slang(event):
    if event.is_group:
        sender = await event.client.get_permissions(event.chat_id, event.sender_id)
        is_admin = sender.is_admin or sender.is_creator

        if not is_admin:
            sentence = event.raw_text
            sent = re.sub(r'\W+', ' ', sentence)
            isslang = False

            for word in sent.split():
                if word.lower() in slang_words:
                    isslang = True
                    await event.delete()
                    sentence = sentence.replace(word, f'||{word}||')

            if isslang and SPOILER:
                name = (await event.get_sender()).first_name
                msgtxt = f"""{name}, ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ᴅᴜᴇ ᴛᴏ ᴛʜᴇ ᴘʀᴇꜱᴇɴᴄᴇ ᴏꜰ ɪɴᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʟᴀɴɢᴜᴀɢᴇ[ɢᴀᴀʟɪ/ꜱʟᴀɴɢꜰᴜʟ ᴡᴏʀᴅꜱ].\n\nʜᴇʀᴇ ɪꜱ ᴀ ᴄᴇɴꜱᴏʀᴇᴅ ᴠᴇʀꜱɪᴏɴ ᴏꜰ ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ:\n\n{sentence}"""
                await event.reply(msgtxt)
