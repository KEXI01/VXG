import functools

# List of admin-only commands
ADMIN_ONLY_COMMANDS = {"/setdelay", "/pretender", "/purge", "/spurge", "/del", "/auth", "/unath"}

def is_admin(func):
    @functools.wraps(func)
    async def a_c(event):
        # Check if the message is a command (starts with '/')
        if not event.text.startswith('/'):
            return  # Ignore non-command messages

        # Extract the command from the message
        command = event.text.split()[0].lower()  # Get the first word (the command)

        # Check if the command is in the list of admin-only commands
        if command in ADMIN_ONLY_COMMANDS:
            is_admin_user = False
            if not event.is_private:
                try:
                    _s = await event.client.get_permissions(event.chat_id, event.sender_id)
                    if _s.is_admin:
                        is_admin_user = True
                except:
                    is_admin_user = False

            if is_admin_user:
                await func(event, _s)  # Execute the command for admins
            else:
                await event.reply("ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ!")
        else:
            await func(event)  # Allow non-admin commands to be executed
    return a_c
