import random
import aiohttp
from io import BytesIO
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from AbhiXMusic import app
from config import BANNED_USERS

# 🔥 STYLISH FONT MAP (Small Caps)
FONT_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ',
    'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
    'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ',
    'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
}

def to_style(text):
    return "".join(FONT_MAP.get(c, c) for c in text)

# 🔥 AI IMAGE GENERATION (Random Seed Added) 🔥

@app.on_message(filters.command(["draw", "imagine", "gen", "art", "ai"]) & ~BANNED_USERS)
async def draw_image(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "🎨 **AI Image Generator**\n\n"
            "**Usage:** `/draw [Prompt]`\n"
            "**Example:** `/draw A cyberpunk boy with fire wings`"
        )

    prompt = message.text.split(None, 1)[1]
    mystic = await message.reply_text("🎨 **Gᴇɴᴇʀᴀᴛɪɴɢ Aʀᴛ...**\n`Pʟᴇᴀsᴇ ᴡᴀɪᴛ...`")

    try:
        # 🔥 Random Seed Logic: Har baar naya URL banega
        seed = random.randint(0, 1000000)
        api_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&width=1024&height=1024&nologo=true"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return await mystic.edit_text("❌ **Eʀʀᴏʀ:** Sᴇʀᴠᴇʀ Bᴜsʏ.")
                
                # Image Downloading
                image_data = await response.read()
                img = BytesIO(image_data)
                img.name = "image.jpg"

        # Stylish Caption
        caption = (
            f"✦ **Aɪ Gᴇɴᴇʀᴀᴛᴇᴅ Aʀᴛ** ✦\n\n"
            f"✨ **Pʀᴏᴍᴘᴛ:** `{prompt}`\n"
            f"👤 **Rᴇǫᴜᴇsᴛᴇᴅ Bʏ:** {message.from_user.mention}\n"
            f"🤖 **Gᴇɴᴇʀᴀᴛᴇᴅ Bʏ:** {to_style(app.name)}"
        )

        await message.reply_photo(
            photo=img,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🗑 Cʟᴏsᴇ", callback_data="close")]]
            )
        )
        await mystic.delete()

    except Exception as e:
        await mystic.edit_text(f"❌ **Eʀʀᴏʀ:** `{e}`")
