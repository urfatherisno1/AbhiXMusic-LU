import logging, sqlite3, datetime, pytz, os, random, asyncio, re
from pyrogram import filters, Client, enums
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import ImageDraw, Image, ImageChops, ImageFont
from groq import Groq

# Groq Setup
GROQ_API_KEY = "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"
client_groq = Groq(api_key=GROQ_API_KEY)
BOSS_ID = 8030201594 

# --- 🖼️ Welcome Image Functions (Consistent with welcome.py) ---
def circle(pfp, size=(825, 824)):
    pfp = pfp.resize(size, Image.LANCZOS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

def welcomepic(pic_path, user_id):
    background_path = "AbhiXMusic/assets/AbhiWel.png"
    font_path = "AbhiXMusic/assets/font.ttf"
    if not os.path.exists(background_path) or not os.path.exists(font_path):
        return None
    
    background = Image.open(background_path)
    pfp = Image.open(pic_path).convert("RGBA")
    pfp = circle(pfp).resize((825, 824))
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype(font_path, size=110)
    draw.text((2100, 1420), f'ID: {user_id}', fill=(255, 255, 255), font=font)
    background.paste(pfp, (1990, 435), pfp)
    output_path = f"downloads/welcome#{user_id}.png"
    background.save(output_path)
    return output_path

async def get_user_details(client, user):
    try:
        full_user = await client.get_chat(user.id)
        bio = full_user.bio if full_user.bio else "No bio available"
        status_map = {"online": "Online", "offline": "Offline", "recently": "Recently"}
        status = status_map.get(user.status, "Recently")
        return bio, status
    except: return "No bio available", "Recently"

# --- 🧠 Database ---
def get_data(user_id):
    try:
        conn = sqlite3.connect('riya_god.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS brain (user_id INTEGER PRIMARY KEY, history TEXT, mood TEXT, warns INTEGER DEFAULT 0)")
        c.execute("SELECT history, mood, warns FROM brain WHERE user_id=?", (user_id,))
        res = c.fetchone()
        conn.close()
        return res if res else ("", "Normal", 0)
    except: return ("", "Normal", 0)

def save_data(user_id, history, mood, warns):
    try:
        conn = sqlite3.connect('riya_god.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO brain VALUES (?, ?, ?, ?)", (user_id, history, mood, warns))
        conn.commit()
        conn.close()
    except: pass

# --- 🌸 1. Detailed Welcome Handler (1 Min Delete) ---
async def riya_welcome_handler(client: Client, event: ChatMemberUpdated):
    if event.new_chat_member and not event.old_chat_member:
        user = event.new_chat_member.user
        if not user or user.is_self: return
        
        chat_id = event.chat.id
        pic_to_use = "AbhiXMusic/assets/AbhiWel.png"
        downloaded_pic = None
        
        try:
            if user.photo:
                downloaded_pic = await client.download_media(user.photo.big_file_id, file_name=f"downloads/pp{user.id}.png")
                pic_to_use = downloaded_pic

            welcome_image = welcomepic(pic_to_use, user.id)
            bio, status = await get_user_details(client, user)
            fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

            # Naya Detailed Caption Format
            caption = f"""
𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 {event.chat.title}
➖➖➖➖➖➖➖➖➖➖➖
🆔 <b>User ID:</b> <code>{user.id}</code>
👤 <b>First Name:</b> {user.first_name}
🗣️ <b>Last Name:</b> {user.last_name if user.last_name else "None"}
🌐 <b>Username:</b> @{user.username if user.username else "None"}
🏛️ <b>DC ID:</b> <code>{user.dc_id if user.dc_id else "Unknown"}</code>
🤖 <b>Is Bot:</b> <code>{user.is_bot}</code>
🚷 <b>Is Scam:</b> <code>{user.is_scam}</code>
✅ <b>Verified:</b> <code>{user.is_verified}</code>
⭐ <b>Premium:</b> <code>{user.is_premium}</code>
📝 <b>User Bio:</b> {bio}
👁️ <b>Last Seen:</b> <code>{status}</code>
🔗 <b>Permanent link:</b> <a href='tg://user?id={user.id}'>{fullname}</a>
➖➖➖➖➖➖➖➖➖➖➖
๏ 𝐌𝐀𝐃𝐄 𝐁𝐘 ➠ [Aʙнɪ 𓆩🇽𓆪 KI𝗡𝗚 📿](https://t.me/imagine_iq)
"""
            sent_msg = await client.send_photo(
                chat_id,
                photo=welcome_image,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⦿ ᴀᴅᴅ ᴍᴇ ⦿", url="https://t.me/RockXMusic_Robot?startgroup=true")]])
            )
            
            if welcome_image and os.path.exists(welcome_image): os.remove(welcome_image)
            if downloaded_pic and os.path.exists(downloaded_pic): os.remove(downloaded_pic)
            
            await asyncio.sleep(60) # 1 Minute delay
            await sent_msg.delete()
            
        except Exception as e:
            logging.error(f"Detailed Welcome Error: {e}")

# --- 2. Main Chat Handler ---
async def riya_chat_handler(client: Client, message: Message):
    if not message or not message.from_user or message.from_user.is_self: return
    user_text, user_id = message.text or "", message.from_user.id
    raw_name = message.from_user.first_name or "Yaar"
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', raw_name).strip() or "Bhai"
    history, mood, warns = get_data(user_id)
    bot_info = await client.get_me()

    if not (str(message.chat.type).split('.')[-1] == "PRIVATE" or 
            any(x in user_text.lower() for x in ["riya", "riyu"]) or 
            (message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id)):
        return

    is_tech = any(x in user_text.lower() for x in ["code", "python", "mcq", "history", "study"])

    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        identity = f"User BOSS Abhi (@FcKU4Baar) hai." if user_id == BOSS_ID else f"User '{clean_name}' hai."
        system_role = (f"Tu Riya hai. {identity} Context: {history}\n"
                       "Rules: 1. Tech query DETAIL. 2. Chatting 3-6 words + 1-2 emojis.")
        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": system_role}, {"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile", temperature=0.8, max_tokens=800 if is_tech else 60
        )
        reply = chat_completion.choices[0].message.content.strip()
        save_data(user_id, (history + f" | U: {user_text} | R: {reply}")[-500:], mood, warns)
        await message.reply_text(reply)
    except: pass

async def start_riya_chatbot():
    if not os.path.exists("downloads"): os.makedirs("downloads")
    logging.info("Riya v50.0 (Detailed Photo Welcome) Activated! 🚀✨")
