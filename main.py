import sys
import glob
import asyncio
import logging
import importlib.util
import urllib3
from pathlib import Path
from config import BOT1, BOT2  # Import both bot instances

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_plugins(plugin_name, bot_instance):
    path = Path(f"src/modules/{plugin_name}.py")
    try:
        spec = importlib.util.spec_from_file_location(f"src.modules.{plugin_name}", path)
        load = importlib.util.module_from_spec(spec)
        load.logger = logging.getLogger(plugin_name)
        spec.loader.exec_module(load)
        sys.modules[f"src.modules.{plugin_name}"] = load
        
        # Register plugin with the specific bot instance
        if hasattr(load, 'register_handlers'):
            load.register_handlers(bot_instance)
            
        print(f"Successfully imported {plugin_name} for {bot_instance._self_name or 'bot'}")
    except Exception as e:
        print(f"Failed to load plugin {plugin_name} for {bot_instance._self_name or 'bot'}: {e}")

async def initialize_bots():
    # Load plugins for both bots
    files = glob.glob("src/modules/*.py")
    
    for name in files:
        patt = Path(name)
        plugin_name = patt.stem
        
        # Skip __init__ files
        if plugin_name.startswith("__"):
            continue
            
        # Load plugin for BOT1
        load_plugins(plugin_name, BOT1)
        
        # Load plugin for BOT2
        load_plugins(plugin_name, BOT2)
    
    print("\nBoth bots have been deployed successfully")

async def run_bots():
    # Create tasks for both bots
    bot1_task = asyncio.create_task(BOT1.run_until_disconnected())
    bot2_task = asyncio.create_task(BOT2.run_until_disconnected())
    
    # Wait for both tasks to complete
    await asyncio.gather(bot1_task, bot2_task)

async def main():
    await initialize_bots()
    try:
        await run_bots()
    except Exception as e:
        logging.error(f"Error in bot operation: {e}")
    finally:
        # Cleanup if needed
        pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nShutting down both bots...")
    finally:
        loop.close()
