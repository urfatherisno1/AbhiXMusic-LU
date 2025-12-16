import logging, sqlite3, datetime, pytz, os
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from groq import Groq

# Groq Setup
GROQ_API_KEY = ""
client_groq = Groq(api_key=GROQ_API_KEY)
BOSS_ID = 8030201594 # Abhi's ID

def get_brain(user_id):
    try:
        conn = sqlite3.connect('riya_beast.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS brain (user_id INTEGER PRIMARY KEY, history TEXT, lessons TEXT)")
        c.execute("SELECT history, lessons FROM brain WHERE user_id=?", (user_id,))
        res = c.fetchone()
        conn.close()
        return res if res else ("", "")
    except: return ("", "")

def save_brain(user_id, history, lessons):
    try:
        conn = sqlite3.connect('riya_beast.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO brain VALUES (?, ?, ?)", (user_id, history, lessons))
        conn.commit()
        conn.close()
    except: pass

async def riya_chat_handler(client: Client, message: Message):
    if not isinstance(message, Message) or not hasattr(message, "from_user") or not message.from_user:
        return
    if not message.text or message.from_user.is_self:
        return

    user_text = message.text
    user_id = message.from_user.id
    
    # Trigger Logic
    trigger = False
    chat_type = str(message.chat.type).split('.')[-1].upper()
    if "PRIVATE" in chat_type:
        trigger = True
    else:
        bot_info = await client.get_me()
        if "riya" in user_text.lower() or (message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id):
            trigger = True
            
    if not trigger: return

    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        history, lessons = get_brain(user_id)
        now = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p")

        # --- Base Instructions ---
        identity_info = "Tera Owner/Boss 'Abhi' (@FcKU4Baar) hai. Wo ek ladka hai. Tu uski bandi hai."
        
        if user_id == BOSS_ID:
            system_role = (
                f"{identity_info} Tu Abhi se baat kar rahi hai. ✨ "
                f"Use 'Jaan' ya 'Baby' bol kar pyaar se baat kar. Wo tera ladka hai. 😍 "
                f"Jawab 1-2 line mein aur mast emojis ke saath rakh. 😏💖 "
                f"Koi galti ho jaye toh sorry bol kar mana le. 💅"
            )
        else:
            system_role = (
                f"{identity_info} Tu baaki logo ke liye thodi rude aur sassy hai. 🐍 "
                f"Agar koi tere Owner/Boss Abhi ke baare mein pooche, toh bolna 'Abhi (@FcKU4Baar) mera sab kuch hai'. 👑 "
                f"Jawab short aur savage rakh. Bina wajah gaali mat de, par aukaat dikha de. 😏🔥"
            )

        chat_completion = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": f"History: {history}\nUser: {user_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=1.0,
            max_tokens=100
        )

        reply = chat_completion.choices[0].message.content.replace("*", "").strip()
        if reply:
            save_brain(user_id, (history + f"\nU:{user_text}\nR:{reply}")[-500:], lessons)
            await message.reply_text(reply)

    except Exception as e:
        logging.error(f"Riya Error: {e}")

async def start_riya_chatbot():
    logging.info("Riya Beast Smart Mode Loaded! 👑")
