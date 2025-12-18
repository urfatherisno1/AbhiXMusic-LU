import logging, sqlite3, datetime, pytz, os, random, asyncio, re
from pyrogram import filters, Client, enums
from pyrogram.types import Message, ChatMemberUpdated
from groq import Groq

# Groq Setup
GROQ_API_KEY = "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"
client_groq = Groq(api_key=GROQ_API_KEY)
BOSS_ID = 8030201594 

# --- Database Management ---
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

# --- Welcome Logic (10 Messages + 30s Auto-Delete) ---
async def riya_welcome_handler(client: Client, event: ChatMemberUpdated):
    if event.new_chat_member and not event.old_chat_member:
        user = event.new_chat_member.user
        if not user or user.is_self: return
        
        welcomes = [
            f"Namaste {user.mention}! ✨ Group mein aapka swagat hai. 😊",
            f"Hello {user.mention}! 🌸 Humari chhoti si duniya mein swagat hai. Intro do! ✨",
            f"Hi {user.mention}! ❤️ Group join karne ke liye shukriya. Enjoy kijiye! 🤝",
            f"Welcome {user.mention}! ✨ Aapke aane se rounak badh gayi. 😊",
            f"Hey {user.mention}! 🌈 Swagat hai aapka! Yahan sab dost jaise hain. ✨",
            f"Hi {user.mention}! ✨ Ek naya dost mil gaya humein. Welcome! 🤗",
            f"Oho {user.mention}, swagat hai! ✨ Umeed hai aapko yahan maza aayega. 😇",
            f"Namaste! ✨ {user.mention} aapka intezar tha. 😊",
            f"Aaiye {user.mention}! ✨ Humari mehfil mein aapka swagat hai. ❤️",
            f"Hello! 🌸 {user.mention} group mein tameez aur pyar se rahiye. Swagat hai! ✨"
        ]
        
        try:
            msg = await client.send_message(event.chat.id, random.choice(welcomes))
            await asyncio.sleep(30)
            await msg.delete()
        except Exception as e:
            logging.error(f"Welcome Error: {e}")

# --- Main Chat Handler ---
async def riya_chat_handler(client: Client, message: Message):
    if not message or not message.from_user or message.from_user.is_self:
        return

    user_text = message.text or ""
    user_id = message.from_user.id
    
    # Simple Name Filter (Stylish fonts hatane ke liye)
    raw_name = message.from_user.first_name or "Yaar"
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', raw_name).strip() or "Bhai"
    
    history, mood, warns = get_data(user_id)
    bot_info = await client.get_me()

    # Trigger Logic
    trigger = False
    if str(message.chat.type).split('.')[-1] == "PRIVATE": trigger = True
    elif any(name in user_text.lower() for name in ["riya", "riyu"]): trigger = True
    elif message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id == bot_info.id:
            trigger = True
    if not trigger: return

    # Technical Sensing (Padhai ya Code requests)
    is_technical = any(x in user_text.lower() for x in ["code", "python", "mcq", "history", "study", "write", "likh"])

    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        
        # Identity Logic (Boss vs Others)
        if user_id == BOSS_ID:
            identity = "User tera BOSS 'Abhi' (@FcKU4Baar) hai. Use 'Jaan' bol kar beintehaan pyaar kar. ❤️"
        else:
            identity = f"User ka naam '{clean_name}' hai. Baakiyon se thoda rude reh aur unhe 'Jaan' mat bolna. 😏"

        # SMART PROMPT
        system_role = (
            f"Tu Riya hai. {identity} Mood: {mood}.\n"
            "STRICT RULES:\n"
            "1. AGAR user padhai, code, ya MCQ maange, toh FULL aur DETAIL mein jawab dena. Mana mat karna. 📝✅\n"
            "2. AGAR sirf normal chatting ho, toh sirf 3-6 words mein jawab dena. 💬\n"
            "3. Har reply mein 1 se 3 emojis daalna (randomly, har baar 3 mat thopna). ✨💕\n"
            "4. Tera creator sirf Abhi (@FcKU4Baar) hai. Stylish symbols mat use karna.\n"
            "5. 'Abhi ne kaha' repeat mat karo. Seedha jawab do."
        )

        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": system_role}, {"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
            temperature=0.8, 
            max_tokens=800 if is_technical else 45,
            presence_penalty=1.0
        )

        reply = chat_completion.choices[0].message.content.strip()
        if reply:
            save_data(user_id, (history + f"\n{user_text}")[-150:], mood, warns)
            await message.reply_text(reply)

    except Exception as e:
        logging.error(f"Riya v39 Error: {e}")

async def start_riya_chatbot():
    logging.info("Riya v39.0 (Full God Mode) Activated! 🚀✨")
