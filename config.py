import os
import logging
from telethon import TelegramClient
from os import getenv
from strings.helpers import DEV
from dotenv import load_dotenv

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

API_ID = 18136872
API_HASH = "312d861b78efcd1b02183b2ab52a83a4"

# Load environment variables
load_dotenv()

# Load values from environment variables
OWNER_ID = int(getenv("OWNER_ID", default="6257927828"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", default="6257927828").split()))
SUDO_USERS.append(OWNER_ID)
SUDO_USERS.extend(DEV)  # Add DEV users if any

SPOILER_MODE = os.environ.get("SPOILER_MODE", "True").lower() == "true"
MONGO_URI = "mongodb+srv://kunaalkumar0091:6qhyyQIyS2idoGFQ@cluster0.z2jge.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "kunaalkumar0091"
LOGGER = False
BOT_NAME = "Guardify"
SUPPORT_ID = -1002440907656
BOT_TOKEN = getenv("BOT_TOKEN", default=None)

# Initialize the bot client
BOT = TelegramClient('ꜱ ᴛ ᴏ ʀ ᴍ', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
