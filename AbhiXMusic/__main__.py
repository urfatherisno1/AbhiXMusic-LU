import asyncio
import importlib
from sys import argv
from pyrogram import idle, filters
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AbhiXMusic import LOGGER, app, userbot
from AbhiXMusic.core.call import Hotty
from AbhiXMusic.misc import sudo
from AbhiXMusic.plugins import ALL_MODULES
from AbhiXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# Riya Imports (Detailed Welcome + Smart Memory)
from AbhiXMusic.plugins.tools.chatbot import start_riya_chatbot, riya_chat_handler, riya_welcome_handler

async def init():
    # Assistant Session Check
    if not any([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
        
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users: BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users: BANNED_USERS.add(user_id)
    except: pass
    
    # Force Stop Auto-Leave (Double Security)
    config.AUTO_LEAVING_ASSISTANT = False

    await app.start()

    # --- Riya Activation ---
    try:
        await start_riya_chatbot()
        app.add_handler(MessageHandler(riya_chat_handler, filters.text & ~filters.regex(r"^/") & ~filters.me), group=-1)
        app.add_handler(ChatMemberUpdatedHandler(riya_welcome_handler), group=-2)
        LOGGER("AbhiXMusic").info("Riya v50.0 (Detailed Photo Welcome) Live! 👑")
    except Exception as ex:
        LOGGER("AbhiXMusic").error(f"Riya Startup Error: {ex}")

    # Plugins Load (Original Music Bot Sequence)
    for all_module in ALL_MODULES:
        importlib.import_module("AbhiXMusic.plugins" + all_module)
    LOGGER("AbhiXMusic.plugins").info("Successfully Imported Modules...")
    
    await userbot.start()
    await Hotty.start()
    
    # Assistant Stay Logic
    try:
        await Hotty.stream_call("https://graph.org/file/e999c40cb700e7c684b75.mp4")
    except NoActiveGroupCall:
        LOGGER("AbhiXMusic").error("Please turn on the videochat of your log group.")
    except: pass
    
    await Hotty.decorators()
    
    LOGGER("AbhiXMusic").info("Bot is Live! Assistant Fixed Forever. @FcKU4Baar")
    
    await idle()
    await app.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
