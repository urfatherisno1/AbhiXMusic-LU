import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from AbhiXMusic import app
from shazamio import Shazam

# 🔥 SHAZAM / SONG IDENTIFIER FEATURE 🔥

@app.on_message(filters.command(["identify", "shazam", "whatsong", "who"]) & filters.group)
async def shazam_check(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ **Reply to an audio or video to identify the song!**")
    
    if not (message.reply_to_message.audio or message.reply_to_message.voice or message.reply_to_message.video):
        return await message.reply_text("❌ **Please reply to a valid Audio or Video file.**")

    mystic = await message.reply_text("🎵 **Listening & Identifying...**\n`Please wait a few seconds...`")
    
    try:
        # File download path
        file_path = await client.download_media(message.reply_to_message)
        
        # Shazam logic
        shazam = Shazam()
        out = await shazam.recognize(file_path)
        
        # File delete kar do space bachane ke liye
        os.remove(file_path)

        # Agar song nahi mila
        if not out.get("track"):
            return await mystic.edit_text("❌ **Couldn't identify the song.**\n`Try a clearer audio clip.`")

        # Data extract
        track = out.get("track")
        title = track.get("title")
        artist = track.get("subtitle")
        image = track.get("images", {}).get("coverart")
        link = track.get("share", {}).get("href")
        
        # Text formatting
        text = (
            f"🎵 **Sᴏɴɢ Iᴅᴇɴᴛɪғɪᴇᴅ!**\n\n"
            f"📌 **Tɪᴛʟᴇ:** {title}\n"
            f"👨‍🎤 **Aʀᴛɪsᴛ:** {artist}\n\n"
            f"🔍 **Pᴏᴡᴇʀᴇᴅ Bʏ:** {app.mention}"
        )

        # Buttons
        buttons = [
            [
                InlineKeyboardButton("🎧 Oᴘᴇɴ Oɴ Sʜᴀᴢᴀᴍ", url=link),
                InlineKeyboardButton("🎵 Pʟᴀʏ Tʜɪs", callback_data=f"slider B|0|{title} {artist}|{message.from_user.id}|g|d")
            ],
            [
                InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close")
            ]
        ]

        await mystic.delete()
        
        if image:
            await message.reply_photo(
                photo=image,
                caption=text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except Exception as e:
        await mystic.edit_text(f"❌ **Error:** `{e}`")
        # Error aane par file delete karna mat bhoolna
        if os.path.exists(file_path):
            os.remove(file_path)
