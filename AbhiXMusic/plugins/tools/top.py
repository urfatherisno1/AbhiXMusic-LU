import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from AbhiXMusic import app
from AbhiXMusic.utils.database import get_global_tops, get_particulars
from AbhiXMusic.utils.decorators.language import language
from config import BANNED_USERS

@app.on_message(filters.command(["top", "toptracks", "globalstats"]) & ~BANNED_USERS)
@language
async def global_stats(client, message, _):
    await message.reply_text(
        "📊 **Tᴏᴘ Pʟᴀʏᴇᴅ Mᴜsɪᴄ Sᴛᴀᴛs**\n\n"
        "Cʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ᴛʜᴇ ᴍᴏsᴛ ᴘʟᴀʏᴇᴅ ᴛʀᴀᴄᴋs ᴏɴ ᴛʜᴇ ʙᴏᴛ.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🌍 Gʟᴏʙᴀʟ Tᴏᴘ 10", callback_data="stats_global"),
                    InlineKeyboardButton("🏠 Gʀᴏᴜᴘ Tᴏᴘ 10", callback_data="stats_group"),
                ],
                [
                    InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close"),
                ]
            ]
        )
    )

@app.on_callback_query(filters.regex("stats_global") & ~BANNED_USERS)
@language
async def show_global_stats(client, CallbackQuery, _):
    stats = await get_global_tops()
    if not stats:
        return await CallbackQuery.answer("❌ Nᴏ ɢʟᴏʙᴀʟ ᴅᴀᴛᴀ ғᴏᴜɴᴅ!", show_alert=True)
    
    # Filter invalid entries
    valid_stats = {k: v for k, v in stats.items() if isinstance(v, dict) and 'spot' in v}
    
    if not valid_stats:
        return await CallbackQuery.answer("❌ Nᴏ ᴠᴀʟɪᴅ ɢʟᴏʙᴀʟ sᴛᴀᴛs ғᴏᴜɴᴅ!", show_alert=True)

    sorted_stats = sorted(valid_stats.items(), key=lambda item: item[1]['spot'], reverse=True)
    
    text = "🌍 **Gʟᴏʙᴀʟ Tᴏᴘ 10 Pʟᴀʏᴇᴅ Sᴏɴɢs**\n\n"
    count = 0
    for vidid, data in sorted_stats:
        count += 1
        if count > 10:
            break
        title = data['title'][:35]
        if title == "Unknown":
            title = "Unknown Track"
        text += f"**{count}.** {title} — `{data['spot']}` Pʟᴀʏs\n"
        
    await CallbackQuery.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="stats_back")]]
        )
    )

@app.on_callback_query(filters.regex("stats_group") & ~BANNED_USERS)
@language
async def show_group_stats(client, CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    stats = await get_particulars(chat_id)
    if not stats:
        return await CallbackQuery.answer("❌ Nᴏ ᴅᴀᴛᴀ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
    
    # Filter invalid entries
    valid_stats = {k: v for k, v in stats.items() if isinstance(v, dict) and 'spot' in v}
    
    if not valid_stats:
        return await CallbackQuery.answer("❌ Nᴏ ᴠᴀʟɪᴅ sᴛᴀᴛs ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)

    sorted_stats = sorted(valid_stats.items(), key=lambda item: item[1]['spot'], reverse=True)
    
    text = "🏠 **Tᴏᴘ 10 Sᴏɴɢs ɪɴ ᴛʜɪs Gʀᴏᴜᴘ**\n\n"
    count = 0
    for vidid, data in sorted_stats:
        count += 1
        if count > 10:
            break
        title = data['title'][:35]
        if title == "Unknown":
            title = "Unknown Track"
        text += f"**{count}.** {title} — `{data['spot']}` Pʟᴀʏs\n"

    await CallbackQuery.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="stats_back")]]
        )
    )

@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@language
async def stats_back(client, CallbackQuery, _):
    await CallbackQuery.edit_message_text(
        "📊 **Tᴏᴘ Pʟᴀʏᴇᴅ Mᴜsɪᴄ Sᴛᴀᴛs**\n\n"
        "Cʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ᴛʜᴇ ᴍᴏsᴛ ᴘʟᴀʏᴇᴅ ᴛʀᴀᴄᴋs ᴏɴ ᴛʜᴇ ʙᴏᴛ.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🌍 Gʟᴏʙᴀʟ Tᴏᴘ 10", callback_data="stats_global"),
                    InlineKeyboardButton("🏠 Gʀᴏᴜᴘ Tᴏᴘ 10", callback_data="stats_group"),
                ],
                [
                    InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close"),
                ]
            ]
        )
    )
