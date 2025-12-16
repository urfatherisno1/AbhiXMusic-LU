import logging, sqlite3, datetime, pytz, os
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from groq import Groq

# Groq Setup
GROQ_API_KEY = "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"
client_groq = Groq(api_key=GROQ_API_KEY)
BOSS_ID = 8030201594 # Teri ID fix hai

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

        # --- Boss vs Others Logic ---
        if user_id == BOSS_ID:
            # Boss ke liye Sweet & Sassy
            system_role = (
                f"Tu Riya hai, Boss Abhi ki pyari psycho bandi. ✨ "
                f"Niyam: "
                f"1. Boss Abhi ko kabhi gaali mat de, hamesha pyaar aur masti se baat kar. 😍 "
                f"2. Jawab short rakh (1-2 line) aur emojis use kar. ✨😏 "
                f"3. Ajay ka naam aaye toh hi gaali de, varna normal reh. 💅 "
                f"4. Boss se 'Boss' ya 'Jaan' bol kar baat kar sakti hai."
            )
        else:
            # Dusro ke liye Destroyer
            system_role = (
                f"Tu Riya hai, ek nider aur bad-maseez ladki. 💅 "
                f"Niyam: "
                f"1. Bina wajah gaali mat de, par rude reh. 🐍 "
                f"2. Ajay ka naam sunte hi uski maa-behen ek kar de. 🤬 "
                f"3. Emojis use kar par acting (*) mat kar. 😏 "
                f"4. Kisi ko bhi 'Randi' ya itni gandi gaali mat de jab tak wo shuruat na kare."
            )

        chat_completion = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": f"History: {history}\nUser: {user_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=1.0, # Temperature thoda kam kiya taaki pagal na ho
            max_tokens=100
        )

        reply = chat_completion.choices[0].message.content.replace("*", "").strip()
        if reply:
            save_brain(user_id, (history + f"\nU:{user_text}\nR:{reply}")[-500:], lessons)
            await message.reply_text(reply)

    except Exception as e:
        logging.error(f"Riya Error: {e}")

async def start_riya_chatbot():
    logging.info("Riya Beast Final Mode Loaded! 🔥")
