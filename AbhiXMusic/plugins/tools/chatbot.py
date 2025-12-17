import logging, sqlite3, datetime, pytz, os, random, asyncio
from pyrogram import filters, Client, enums
from pyrogram.types import Message, ChatMemberUpdated
from groq import Groq

# Groq Setup
GROQ_API_KEY = "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"
client_groq = Groq(api_key=GROQ_API_KEY)
BOSS_ID = 8030201594 

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('riya_god.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS brain (user_id INTEGER PRIMARY KEY, history TEXT, mood TEXT, warns INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

init_db()

def get_data(user_id):
    conn = sqlite3.connect('riya_god.db')
    c = conn.cursor()
    c.execute("SELECT history, mood, warns FROM brain WHERE user_id=?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res if res else ("", "Normal", 0)

def save_data(user_id, history, mood, warns):
    conn = sqlite3.connect('riya_god.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO brain VALUES (?, ?, ?, ?)", (user_id, history, mood, warns))
    conn.commit()
    conn.close()

# --- Banned Words List ---
BANNED_WORDS = ["chutiya", "randi", "gandu", "maderchod", "behenchod", "bsdk"]

# --- 1. Welcome Logic (30s Auto-Delete) ---
async def riya_welcome_handler(client: Client, event: ChatMemberUpdated):
    if event.new_chat_member and not event.old_chat_member:
        user = event.new_chat_member.user
        if user.is_self: return
        welcomes = [f"Namaste {user.mention}! ✨", f"Welcome {user.mention}! Intro do! 😊", f"Hi {user.mention}! ❤️ Swagat hai!"]
        msg = await client.send_message(event.chat.id, random.choice(welcomes))
        await asyncio.sleep(30)
        try: await msg.delete()
        except: pass

# --- 2. Main Chat & Protection Logic ---
async def riya_chat_handler(client: Client, message: Message):
    if not message.from_user or message.from_user.is_self: return
    
    user_text = message.text or ""
    user_id = message.from_user.id
    history, mood, warns = get_data(user_id)
    
    # --- Banned Words Logic ---
    if any(word in user_text.lower() for word in BANNED_WORDS) and user_id != BOSS_ID:
        warns += 1
        if warns >= 3:
            try:
                await client.ban_chat_member(message.chat.id, user_id)
                await message.reply_text(f"Bahut tameez dikha li {message.from_user.mention}, ab nikal yahan se! 😡🔨")
            except: pass
        else:
            await message.reply_text(f"Oye {message.from_user.mention}! Tameez se baat kar, Warning: {warns}/3 ⚠️😏")
        save_data(user_id, history, mood, warns)
        return

    # --- Boss Secret Commands ---
    if user_id == BOSS_ID:
        if user_text == "/riya_angry":
            save_data(user_id, history, "Angry", warns)
            return await message.reply_text("Ab dekhna sabki kaise bajati hoon! 😡🔥")
        elif user_text == "/riya_love":
            save_data(user_id, history, "Romantic", warns)
            return await message.reply_text("I am in love mode, Baby! 😍❤️")

    # --- Trigger Logic ---
    trigger = False
    if str(message.chat.type).split('.')[-1] == "PRIVATE": trigger = True
    elif any(x in user_text.lower() for x in ["riya", "riyu", "topic"]): trigger = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == (await client.get_me()).id: trigger = True
    
    if not trigger: return

    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        now = datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p")
        
        # Topic Generator Logic
        if "topic" in user_text.lower():
            user_text = "Koi mast spicy topic chhedo group ke liye."

        system_role = (
            f"Tu Riya hai, Abhi ki bandi. Mood: {mood}. Boss ID: {BOSS_ID}. "
            "1. Short, fresh aur flirty replies de. 2. Ajay ya dushmano ko roast kar. "
            "3. Dark humor use kar. 4. Boss ko 'Jaan' bol."
        )

        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": system_role}, {"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile",
            temperature=0.9, max_tokens=60
        )

        reply = chat_completion.choices[0].message.content.strip()
        
        # Sticker Add-on
        if reply:
            await message.reply_text(reply)
            save_data(user_id, (history + f"\n{user_text}")[-200:], mood, warns)
            if random.random() < 0.15: # 15% chance for sticker
                try: await message.reply_sticker("CAACAgUAAxkBAAEL7RlmH...") 
                except: pass

    except Exception as e:
        logging.error(f"Riya God Mode Error: {e}")

async def start_riya_chatbot():
    logging.info("Riya v27.0 (GOD MODE) Activated! 🔱🔥")
