import aiohttp
from io import BytesIO
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from AbhiXMusic import app
from config import BANNED_USERS

# 🔥 AI IMAGE GENERATION FEATURE (Fixed Upload) 🔥

@app.on_message(filters.command(["draw", "imagine", "gen", "art", "ai"]) & ~BANNED_USERS)
async def draw_image(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "🎨 **AI Text to Image Generator**\n\n"
            "**Usage:** `/draw [Prompt]`\n"
            "**Example:** `/draw A cyberpunk boy with fire wings`"
        )

    # Prompt ko URL safe banane ki jarurat nahi, hum direct request karenge
    prompt = message.text.split(None, 1)[1]
    mystic = await message.reply_text("🎨 **Generating Image...**\n`Please wait...`")

    try:
        # Pollinations.ai API
        api_url = f"https://image.pollinations.ai/prompt/{prompt}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return await mystic.edit_text("❌ **Error:** Server is busy, try again later.")
                
                # Image ko bytes (memory) me download karna
                image_data = await response.read()
                img = BytesIO(image_data)
                img.name = "image.jpg" # Telegram ko filename batana jaruri hai

        # Ab image file ko upload karenge (Direct URL nahi denge)
        await message.reply_photo(
            photo=img,
            caption=f"🎨 **Generated:** `{prompt}`\n🤖 **By:** {app.mention}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Close", callback_data="close")]]
            )
        )
        await mystic.delete()

    except Exception as e:
        await mystic.edit_text(f"❌ **Error:** `{e}`")
