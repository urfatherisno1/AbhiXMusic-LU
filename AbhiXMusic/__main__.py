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

# Riya Imports (v48.0)
from AbhiXMusic.plugins.tools.chatbot import start_riya_chatbot, riya_chat_handler, riya_welcome_handler

async def init():
    # 1. Basic Setup & Banned Users Load
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users: BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users: BANNED_USERS.add(user_id)
    except: pass
    
    # 2. Start Main Bot (App)
    await app.start() 
    
    # 3. --- Riya System Activation ---
    try:
        await start_riya_chatbot()
        # Riya Handlers Setup
        app.add_handler(MessageHandler(riya_chat_handler, filters.text & ~filters.regex(r"^/") & ~filters.me), group=-1)
        app.add_handler(ChatMemberUpdatedHandler(riya_welcome_handler), group=-2)
        LOGGER("AbhiXMusic").info("Riya v48.0 (Super Memory) Live! 👑")
    except Exception as ex:
        LOGGER("AbhiXMusic").error(f"Riya Startup Error: {ex}")

    # 4. Load Music Plugins
    for all_module in ALL_MODULES:
        importlib.import_module("AbhiXMusic.plugins" + all_module)
    LOGGER("AbhiXMusic.plugins").info("Successfully Imported Modules...")
    
    # 5. Start Assistant & Call Core
    await userbot.start() 
    await Hotty.start() 
    
    # 6. --- FIX: Assistant Invite & Stream Call ---
    try:
        # Ye line assistant ko group mein invite karne aur active rakhne mein madad karegi
        await Hotty.stream_call("https://graph.org/file/e999c40cb700e7c684b75.mp4")
    except NoActiveGroupCall:
        LOGGER("AbhiXMusic").error("Please turn on the videochat of your log group/channel.")
    except Exception as e:
        LOGGER("AbhiXMusic").error(f"Stream Call Error: {e}")
    
    # 7. Start Decorators (Auto-Leave/Auto-Invite logic)
    try:
        await Hotty.decorators()
        LOGGER("AbhiXMusic").info("Hotty Decorators Started! ✅")
    except Exception as e:
        LOGGER("AbhiXMusic").error(f"Decorators Error: {e}")
    
    LOGGER("AbhiXMusic").info("Bot is Live! @FcKU4Baar")
    
    # 8. Idle till Stop
    await idle() 
    await app.stop()
    await userbot.stop()
    LOGGER("AbhiXMusic").info("Stopping AbhiXMusic Bot...")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
