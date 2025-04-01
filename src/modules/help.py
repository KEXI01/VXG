from telethon import events
from telethon.tl.custom import Button
from config import BOT

media_msg = f"""
**•─╼⃝𖠁 ᴍᴇᴅɪᴀ ɢ ᴄᴏᴍᴍᴀɴᴅꜱ: 𖠁⃝╾─•**

🔸 ᴍᴀɴʏ ᴄᴏᴍᴍᴀɴᴅꜱ ᴏᴘᴇʀᴀᴛᴇ ɪɴ ᴀ ᴘᴀꜱꜱɪᴠᴇ ᴏʀ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴍᴀɴɴᴇʀ

🔸/setdelay - ᴅᴇʟᴇᴛᴇᴅ ᴍᴇᴅɪᴀ ɪɴ ᴄʜᴀᴛ

"""

edit_msg = f"""
**•─╼⃝𖠁 ᴇᴅɪᴛ ɢ ᴄᴏᴍᴍᴀɴᴅꜱ: 𖠁⃝╾─•**

🔸 /auth - ᴀᴜᴛʜ ᴀ ᴜꜱᴇʀ ɪɴ ᴄʜᴀᴛ ᴛᴏ ᴘʀᴇᴠᴇɴᴛ ᴅᴇʟᴇᴛɪᴏɴ

🔸 /unauth - ᴜɴᴀᴜᴛʜ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴀʟʟᴏᴡ ᴍᴇꜱꜱᴀɢᴇ

🔸 /authusers - ꜱʜᴏᴡꜱ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜꜱᴇʀꜱ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ (ᴏᴡɴᴇʀ ᴏɴʟʏ)

🔸 /id -  ɢᴇᴛ ᴜꜱᴇʀ ɪᴅ ᴏғ ᴜꜱᴇʀ ʙʏ ʀᴇᴘʟʏɪɴɢ ʜɪᴍ/ʜᴇʀ ᴍꜱɢ

🔸 /getid - ɢᴇᴛ ᴜꜱᴇʀ ɪᴅ ᴏғ ᴜꜱᴇʀ ᴏʀ ᴄʜᴀᴛ

🔸 /stats - ꜱᴛᴀᴛɪᴛɪᴄꜱ ᴏғ ʙɪʟʟᴀ ᴇɢ

🔸 /activegroups - ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ ɢᴄ'ꜱ ᴡʜᴇʀᴇ ʙɪʟʟᴀ ɪꜱ

🔸 /clone -  ᴍᴀᴋᴇ ʏᴏᴜʀ ᴏᴡɴ ʙɪʟʟᴀ ɢᴜᴀʀᴅɪᴀɴ (ᴏᴡɴᴇʀ ᴏɴʟʏ)

🔸/pretender - ᴅᴇᴛᴇᴄᴛ ᴘʀᴇᴛᴇɴᴅᴇʀ
"""       

START_OP = [
    [
      Button.inline("• ᴍᴇᴅɪᴀ ɢ •", data="media"),
      Button.inline("• ᴇᴅɪᴛ ɢ •", data="edit")
    ],
    [
      Button.url("ᴜᴘᴅᴀᴛᴇꜱ", "https://t.me/STORM_TECHH")
    ]
  ]

@BOT.on(events.NewMessage(pattern="/help"))
async def start(event):
    KEX = await event.client.get_me()
    bot_name = KEX.first_name

    if event.is_private:
        TEXT = f"""
<b>✨ •─╼⃝𖠁 ʜᴇʟᴘ ᴍᴇɴᴜ 𖠁⃝╾─• ✨</b>
"""
        await event.respond(TEXT, buttons=START_OP, parse_mode='html')
    else:
        TEXT = "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ꜰᴏʀ ʜᴇʟᴘ!"
        BUTTON = [[Button.url("ʜᴇʟᴘ", f"https://t.me/vxguardian_bot?start=help")]]
        await event.reply(TEXT, buttons=BUTTON, parse_mode='html')


@BOT.on(events.CallbackQuery(pattern=r"media"))
async def help_media(event):
    await event.edit(media_msg,
          buttons=[[Button.inline("🔙 ʙᴀᴄᴋ", data="help_back"),],],
          )

@BOT.on(events.CallbackQuery(pattern=r"edit"))
async def help_edit(event):
    await event.edit(edit_msg,
        buttons=[[Button.inline("🔙 ʙᴀᴄᴋ", data="help_back"),],],
      )

@BOT.on(events.CallbackQuery(pattern=r"help_back"))
async def help_back(event):
    TEXT = f"""
<b>✨ •─╼⃝𖠁 ʜᴇʟᴘ ᴍᴇɴᴜ 𖠁⃝╾─• ✨</b>
"""
    await event.edit(TEXT, buttons=START_OP, parse_mode='html')

@BOT.on(events.NewMessage(pattern="/start help"))
async def start_help(event):
    if event.is_private:
        TEXT = f"""
<b>✨ •─╼⃝𖠁 ʜᴇʟᴘ ᴍᴇɴᴜ 𖠁⃝╾─• ✨</b>
"""
        await event.respond(TEXT, buttons=START_OP, parse_mode='html')
        return
