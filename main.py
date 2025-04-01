import sys
import glob
import asyncio
import logging
import importlib.util
import urllib3
from pathlib import Path
from config import BOT

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_plugins(plugin_name):
    path = Path(f"src/modules/{plugin_name}.py")
    try:
        spec = importlib.util.spec_from_file_location(f"src.modules.{plugin_name}", path)
        load = importlib.util.module_from_spec(spec)
        load.logger = logging.getLogger(plugin_name)
        spec.loader.exec_module(load)
        sys.modules[f"src.modules.{plugin_name}"] = load
        print(f"ꜱᴛᴏʀᴍ ʜᴀꜱ ɪᴍᴘᴏʀᴛᴇᴅ {plugin_name}")
    except Exception as e:
        print(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ʟᴏᴀᴅ ᴘʟᴜɢɪɴ {plugin_name}: {e}")

files = glob.glob("src/modules/*.py")
for name in files:
    patt = Path(name)
    plugin_name = patt.stem
    load_plugins(plugin_name)

print("\nʙᴏᴛ ɪꜱ ᴅᴇᴘʟᴏʏᴇᴅ ꜱᴜᴄᴄᴇꜱꜰᴜʟʟʏ")

async def main():
    tasks = [
        BOT.run_until_disconnected()
    ]
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"ꜱᴛᴏʀᴍ ᴀɪ ꜰᴏᴜɴᴅ ᴀɴ ᴇʀʀᴏʀ ⚠️: {e}")

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()
