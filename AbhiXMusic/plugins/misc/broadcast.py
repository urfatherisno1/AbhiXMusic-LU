import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from AbhiXMusic import app
from AbhiXMusic.misc import SUDOERS
from AbhiXMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from AbhiXMusic.utils.decorators.language import language
from AbhiXMusic.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    
    # --- Flag Detection & Cleaning ---
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    
    # Extract query and clean flags
    if len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    else:
        query = ""

    flags = ["-pin", "-nobot", "-pinloud", "-assistant", "-user", "-f", "-pr"]
    for flag in flags:
        query = query.replace(flag, "")
    query = query.strip()

    # Logic: If NOT replying and query is empty -> Error
    if not message.reply_to_message and query == "":
        return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # --- Setting Modes ---
    force_copy = "-f" in message.text
    disable_preview = "-pr" in message.text
    
    # Helper to send or copy securely
    async def send_or_copy(chat_id, text_query):
        if message.reply_to_message:
            if force_copy:
                # Logic: If it's just TEXT, use send_message to allow disabling preview
                if message.reply_to_message.text:
                    return await app.send_message(
                        chat_id, 
                        text=message.reply_to_message.text, 
                        disable_web_page_preview=disable_preview
                    )
                # Logic: If it's MEDIA, use copy_message (copy_message doesn't support disable_web_page_preview arg)
                else:
                    return await app.copy_message(
                        chat_id, 
                        y, 
                        x,
                        caption=message.reply_to_message.caption
                    )
            else:
                # Normal Forward
                return await app.forward_messages(chat_id, y, x)
        else:
            # Normal Send Message
            return await app.send_message(chat_id, text=text_query, disable_web_page_preview=disable_preview)

    # --- Broadcast to CHATS ---
    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        
        for i in chats:
            try:
                m = await send_or_copy(i, query)
                
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except:
                        continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                continue
                
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except:
            pass

    # --- Broadcast to USERS ---
    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
            
        for i in served_users:
            try:
                await send_or_copy(i, query)
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
                
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except:
            pass

    # --- Broadcast to ASSISTANTS ---
    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from AbhiXMusic.core.userbot import assistants

        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                try:
                    # Same logic for assistants
                    if message.reply_to_message:
                        if force_copy:
                             if message.reply_to_message.text:
                                await client.send_message(dialog.chat.id, text=message.reply_to_message.text, disable_web_page_preview=disable_preview)
                             else:
                                await client.copy_message(dialog.chat.id, y, x)
                        else:
                            await client.forward_messages(dialog.chat.id, y, x)
                    else:
                        await client.send_message(dialog.chat.id, text=query, disable_web_page_preview=disable_preview)
                        
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    flood_time = int(fw.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    continue
            text += _["broad_7"].format(num, sent)
        try:
            await aw.edit_text(text)
        except:
            pass
            
    IS_BROADCASTING = False

async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue

asyncio.create_task(auto_clean())
