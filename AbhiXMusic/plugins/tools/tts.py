import io
import edge_tts
from pyrogram import filters
from AbhiXMusic import app

# 🔥 REALISTIC AI VOICE (Multi-Character Support) 🔥

# Voice Configuration
VOICES = {
    "girl": {
        "hi": "hi-IN-SwaraNeural",  # Hindi Girl
        "en": "en-US-AnaNeural"     # English Girl
    },
    "boy": {
        "hi": "hi-IN-MadhurNeural", # Hindi Boy (Deep Voice)
        "en": "en-US-ChristopherNeural" # English Boy (Attitude)
    }
}

@app.on_message(filters.command(["tts", "speak", "bol"]))
async def text_to_speech(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "🗣️ **AI Voice Generator**\n\n"
            "**Usage:**\n"
            "1. `/tts [Text]` (Default Girl)\n"
            "2. `/tts boy [Text]` (Male Voice)\n"
            "3. `/tts girl [Text]` (Female Voice)\n\n"
            "**Example:**\n"
            "`/tts boy Riya I love you`"
        )

    # Arguments parse karna
    args = message.text.split(None, 1)[1]
    
    # Default settings
    mode = "girl" 
    text = args
    
    # Check karna ki user ne specific voice mangi hai kya?
    first_word = args.split()[0].lower()
    
    if first_word in ["boy", "male", "aadmi"]:
        mode = "boy"
        try:
            text = args.split(None, 1)[1] # "boy" ko text se hata do
        except:
            return await message.reply_text("❌ Are bhai, `boy` ke baad kuch likhna bhi padega na!")
            
    elif first_word in ["girl", "female", "ladki"]:
        mode = "girl"
        try:
            text = args.split(None, 1)[1]
        except:
            return await message.reply_text("❌ Text to likh meri jaan!")

    mystic = await message.reply_text(f"🗣️ **{mode.capitalize()} ki aawaz bana raha hu...**")

    try:
        # Language Detection (Hindi words check)
        # Agar hindi words hain to Hindi voice, warna English
        lang = "hi" if any(x in text.lower() for x in ["kya", "kaise", "ho", "hai", "tum", "main", "hum", "love", "dil"]) else "en"
        
        selected_voice = VOICES[mode][lang]
        
        # Audio Stream Generate
        communicate = edge_tts.Communicate(text, selected_voice)
        
        # Pitch Adjustment for special effects (Optional)
        # Agar boy hai to thoda aur deep karte hain
        if mode == "boy":
            communicate = edge_tts.Communicate(text, selected_voice, pitch="-5Hz", rate="-5%")
            
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        audio_file = io.BytesIO(audio_data)
        audio_file.name = f"{mode}_voice.mp3"

        await message.reply_audio(
            audio=audio_file,
            caption=f"🗣️ **Mode:** {mode.capitalize()} ({lang.upper()})\n👤 **Text:** `{text}`",
            performer="Riya AI",
            title=f"AI Voice ({mode})"
        )
        
        await mystic.delete()

    except Exception as e:
        await mystic.edit_text(f"❌ **Error:** `{e}`")

__HELP__ = """
**🗣️ ᴀɪ ᴠᴏɪᴄᴇ (ᴍᴜʟᴛɪ-ᴄʜᴀʀᴀᴄᴛᴇʀ)**

Use these commands to generate realistic voice messages.

- `/tts <text>` : Default Girl Voice.
- `/tts boy <text>` : Deep Male Voice.
- `/tts girl <text>` : Cute Female Voice.

**Example:**
`/tts boy Suno Riya, tum meri ho!`
"""

__MODULE__ = "TTS"
