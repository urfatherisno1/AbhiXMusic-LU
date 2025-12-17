import logging, sqlite3, datetime, pytz, os, random, asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import Message, ChatMemberUpdated
from groq import Groq

# Groq Setup
GROQ_API_KEY = "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"
client_groq = Groq(api_key=GROQ_API_KEY)
BOSS_ID = 8030201594 

# --- Database Management ---
def get_brain(user_id):
    try:
        conn = sqlite3.connect('riya_final.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS brain (user_id INTEGER PRIMARY KEY, history TEXT, lessons TEXT, mood TEXT)")
        c.execute("SELECT history, lessons, mood FROM brain WHERE user_id=?", (user_id,))
        res = c.fetchone()
        conn.close()
        return res if res else ("", "", "Normal")
    except: return ("", "", "Normal")

def save_brain(user_id, history, lessons, mood):
    try:
        conn = sqlite3.connect('riya_final.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO brain VALUES (?, ?, ?, ?)", (user_id, history, lessons, mood))
        conn.commit()
        conn.close()
    except: pass

# --- Welcome Logic (30 Sec Auto-Delete) ---
async def riya_welcome_handler(client: Client, event: ChatMemberUpdated):
    if event.new_chat_member and not event.old_chat_member:
        user = event.new_chat_member.user
        if user.is_self: return
        
        welcomes = [
            f"Namaste {user.mention}! ✨ Group mein aapka swagat hai. 😊",
            f"Hello {user.mention}! 🌸 Humari chhoti si duniya mein swagat hai. Intro do! ✨",
            f"Hi {user.mention}! ❤️ Group join karne ke liye shukriya. Enjoy kijiye! 🤝",
            f"Welcome {user.mention}! ✨ Aapke aane se rounak badh gayi. 😊"
        ]
        
        try:
            # Message bhejo
            welcome_msg = await client.send_message(event.chat.id, random.choice(welcomes))
            # 30 seconds ruko
            await asyncio.sleep(30)
            # Message delete karo
            await welcome_msg.delete()
        except Exception as e:
            logging.error(f"Welcome Delete Error: {e}")

# --- Chat Logic ---
async def riya_chat_handler(client: Client, message: Message):
    if not isinstance(message, Message) or not hasattr(message, "from_user") or not message.from_user:
        return
    if message.from_user.is_self: return

    user_text = message.text or ""
    user_id = message.from_user.id
    bot_info = await client.get_me()
    
    trigger = False
    chat_type = str(message.chat.type).split('.')[-1].upper()
    
    if "PRIVATE" in chat_type:
        trigger = True
    elif any(name in user_text.lower() for name in ["riya", "riyu"]): 
        trigger = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id:
        trigger = True
            
    if not trigger: return

    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        history, lessons, mood = get_brain(user_id)
        
        if user_id == BOSS_ID:
            system_role = "Tu Riya hai, Abhi ki bandi. 1-2 words mein flirty aur fresh jawab de. ✨😏"
        else:
            system_role = "Tu Riya hai, Abhi ki sassy bandi. Dusron ke liye rude aur short (max 5 words) rehna. 😏🔥"

        chat_completion = client_groq.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": f"History: {history[-150:]}\nUser: {user_text}"} 
            ],
            model="llama-3.3-70b-versatile",
            temperature=1.0,
            max_tokens=40,
            presence_penalty=1.0,
            frequency_penalty=1.0
        )

        reply = chat_completion.choices[0].message.content.replace("*", "").strip()

        if not reply or "Abhi ne sikhaya" in reply:
            reply = random.choice(["Bolo Jaan? 😉", "Hmm? ✨", "Bolo na! ❤️"])

        if reply:
            save_brain(user_id, (history + f"\nU:{user_text}\nR:{reply}")[-300:], lessons, mood)
            await message.reply_text(reply)

    except Exception as e:
        logging.error(f"Riya v26 Error: {e}")

async def start_riya_chatbot():
    logging.info("Riya v26.0 (30s Auto-Delete Welcome) Active! 🚀✨")
