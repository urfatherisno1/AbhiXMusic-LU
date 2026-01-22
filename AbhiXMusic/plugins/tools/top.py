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
        "📊 **Top Played Music Stats**\n\n"
        "Choose an option below to view the most played tracks on the bot.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🌍 Global Top 10", callback_data="stats_global"),
                    InlineKeyboardButton("🏠 Group Top 10", callback_data="stats_group"),
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="close"),
                ]
            ]
        )
    )

@app.on_callback_query(filters.regex("stats_global") & ~BANNED_USERS)
@language
async def show_global_stats(client, CallbackQuery, _):
    stats = await get_global_tops()
    if not stats:
        return await CallbackQuery.answer("❌ No global data found!", show_alert=True)
    
    # 🔥 Fix: Filter invalid entries (ignore bad strings)
    valid_stats = {k: v for k, v in stats.items() if isinstance(v, dict) and 'spot' in v}
    
    if not valid_stats:
        return await CallbackQuery.answer("❌ No valid global stats found!", show_alert=True)

    sorted_stats = sorted(valid_stats.items(), key=lambda item: item[1]['spot'], reverse=True)
    
    text = "🌍 **Global Top 10 Played Songs**\n\n"
    count = 0
    for vidid, data in sorted_stats:
        count += 1
        if count > 10:
            break
        text += f"**{count}.** {data['title'][:35]} — `{data['spot']}` Plays\n"
        
    await CallbackQuery.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="stats_back")]]
        )
    )

@app.on_callback_query(filters.regex("stats_group") & ~BANNED_USERS)
@language
async def show_group_stats(client, CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    stats = await get_particulars(chat_id)
    if not stats:
        return await CallbackQuery.answer("❌ No data for this group!", show_alert=True)
    
    # 🔥 Fix: Filter invalid entries here too
    valid_stats = {k: v for k, v in stats.items() if isinstance(v, dict) and 'spot' in v}
    
    if not valid_stats:
        return await CallbackQuery.answer("❌ No valid stats for this group!", show_alert=True)

    sorted_stats = sorted(valid_stats.items(), key=lambda item: item[1]['spot'], reverse=True)
    
    text = "🏠 **Top 10 Songs in this Group**\n\n"
    count = 0
    for vidid, data in sorted_stats:
        count += 1
        if count > 10:
            break
        text += f"**{count}.** {data['title'][:35]} — `{data['spot']}` Plays\n"

    await CallbackQuery.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="stats_back")]]
        )
    )

@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@language
async def stats_back(client, CallbackQuery, _):
    await CallbackQuery.edit_message_text(
        "📊 **Top Played Music Stats**\n\n"
        "Choose an option below to view the most played tracks.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🌍 Global Top 10", callback_data="stats_global"),
                    InlineKeyboardButton("🏠 Group Top 10", callback_data="stats_group"),
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="close"),
                ]
            ]
        )
    )
