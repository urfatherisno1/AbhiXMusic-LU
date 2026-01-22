import re
import os
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# --- 🔑 DimpiAPI Credentials (UPDATED) ---
API_URL = getenv("API_URL", "https://myloveisdimpi.online/download")
VIDEO_API_URL = getenv("VIDEO_API_URL", "https://myloveisdimpi.online/download")
API_KEY = getenv("API_KEY", "DIMPI-SECRET-KEY")

# --- 🔑 Telegram Credentials ---
API_ID = int(getenv("API_ID", "0")) 
API_HASH = getenv("API_HASH", "YourHash")
BOT_TOKEN = getenv("BOT_TOKEN", "YourToken")

# --- 🗄️ Database & Bot Info ---
MONGO_DB_URI = getenv("MONGO_DB_URI", None)
MUSIC_BOT_NAME = getenv("MUSIC_BOT_NAME", "AbhiXMusic")
PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", None)
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 900))
LOGGER_ID = int(getenv("LOGGER_ID", None)) # Log Channel ID yahan hona chahiye

# --- 👑 Owner ---
OWNER_ID = int(getenv("OWNER_ID", "8030201594"))
SUDOERS = [8030201594, 8257566294]

# --- ☁️ Heroku ---
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# --- 🚀 Links ---
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/ShahinaAbhi143/AbhiXMusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/imagine_iq")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/smart_study_3")

# --- ⚙️ Settings ---
AUTO_LEAVING_ASSISTANT = False
AUTO_GCAST = os.getenv("AUTO_GCAST")
AUTO_GCAST_MSG = getenv("AUTO_GCAST_MSG", "")

# --- 🎵 Spotify ---
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "bcfe26b0ebc3428882a0b5fb3e872473")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "907c6a054c214005aeae1fd752273cc4")

# --- 📊 Limits ---
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "50"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "2000"))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

# --- 🔑 Sessions ---
STRING1 = getenv("STRING_SESSION",  None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_IMG_URL = getenv("START_IMG_URL", "https://graph.org/file/804fa956a84862b547fc5.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://graph.org/file/dc111a1c1358c553ea604.jpg")
PLAYLIST_IMG_URL = "https://graph.org/file/1e0af186d0575a7d6a650.jpg"
STATS_IMG_URL = "https://graph.org/file/83312f735f032270a4c23.jpg"
TELEGRAM_AUDIO_URL = "https://graph.org/file/d8db306e9e0b0504718b3.jpg"
TELEGRAM_VIDEO_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://te.legra.ph/file/6298d377ad3eb46711644.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is wrong.")

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is wrong.")
