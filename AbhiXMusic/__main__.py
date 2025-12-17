import asyncio
import importlib
from pyrogram import idle, filters
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
import config
from AbhiXMusic import LOGGER, app, userbot
from AbhiXMusic.core.call import Hotty
from AbhiXMusic.misc import sudo
from AbhiXMusic.plugins import ALL_MODULES
from AbhiXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# Riya Imports
from AbhiXMusic.plugins.tools.chatbot import start_riya_chatbot, riya_chat_handler, riya_welcome_handler

async def init():
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users: BANNED_USERS.add(user_id)
    except: pass
    
    await app.start() 
    
    try:
        await start_riya_chatbot()
        # Chat Handler
        app.add_handler(MessageHandler(riya_chat_handler, filters.text & ~filters.regex(r"^/") & ~filters.me), group=-1)
        # Welcome Handler
        app.add_handler(ChatMemberUpdatedHandler(riya_welcome_handler), group=-2)
        
        LOGGER(__name__).info("Riya System Started with Auto-Delete Welcome! 👑")
    except Exception as ex:
        LOGGER(__name__).error(f"Riya Startup Error: {ex}")

    for all_module in ALL_MODULES:
        importlib.import_module("AbhiXMusic.plugins" + all_module)
    
    await userbot.start() 
    await Hotty.start() 
    
    LOGGER("AbhiXMusic").info("Bot is Live! @FcKU4Baar")
    await idle() 

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
