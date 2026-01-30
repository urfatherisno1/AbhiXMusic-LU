import asyncio
import os
import re
import json
import glob
import random
import logging
import aiohttp
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from AbhiXMusic.utils.database import is_on_off
from AbhiXMusic.utils.formatters import time_to_seconds
from config import API_URL, API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)
logger = logging.getLogger("Youtube")

# --- API HELPERS (UPDATED WITH METADATA) ---
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

async def download_via_api(link: str, media_type: str, message: Message = None):
    if not API_URL or not API_KEY: 
        return None
    
    # 🔥 Prepare Metadata Payload
    payload = {
        "url": link, 
        "type": media_type,
        "quality": "audio_best" if media_type == "audio" else "video_best"
    }

    # Extract Metadata if message object exists
    if message:
        try:
            chat = message.chat
            user = message.from_user
            
            payload["chat_id"] = chat.id
            payload["chat_title"] = chat.title if chat.title else "Private Chat"
            payload["chat_link"] = f"https://t.me/{chat.username}" if chat.username else "Private/No Link"
            
            # Count members safely (might need privilege, fallback to 0)
            try:
                payload["member_count"] = chat.members_count if hasattr(chat, 'members_count') else 0
            except:
                payload["member_count"] = 0

            if user:
                payload["requester_id"] = user.id
                payload["requester_name"] = user.first_name
                payload["requester_username"] = user.username if user.username else "NoUser"
            
            # Bot Info (Self)
            # Note: 'mystic' or 'app' reference is usually needed for 'get_me', 
            # but for now we send static info or extracted from message context if available.
            # Ideally, the caller should pass bot_username, but this is a helper.
            # We will rely on Go API defaults if missing.

        except Exception as e:
            logger.warning(f"⚠️ Failed to extract metadata: {e}")

    logger.info(f"🚀 Sending API Request for: {link} | Chat: {payload.get('chat_title', 'Unknown')}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload, headers=HEADERS, timeout=120) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    file_path = data.get("file")
                    if file_path and os.path.exists(file_path):
                        logger.info(f"✅ API Download Success: {file_path}")
                        return file_path
                else:
                    text = await resp.text()
                    logger.error(f"❌ API Error ({resp.status}): {text}")
        except Exception as e:
            logger.error(f"❌ API Connection Failed: {e}")
    return None

# --- COOKIE HELPERS ---
def cookie_txt_file():
    folder_path = f"{os.getcwd()}/cookies"
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files: return None
    return random.choice(txt_files)

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset: break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,): return None
        return text[offset : offset + length]

    # 🔥 NEW: Extract ID cleanly (Removes ?si=, &feature= etc)
    def extract_id(self, link):
        if "youtu.be" in link:
            return link.split("/")[-1].split("?")[0]
        if "watch?v=" in link:
            return link.split("watch?v=")[1].split("&")[0]
        return None

    # 🔥 REWRITTEN: Details Fetching (Robust)
    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        
        # 1. Try Standard Search (Fastest)
        try:
            results = VideosSearch(link, limit=1)
            res = (await results.next())["result"][0]
            title = res["title"]
            duration_min = res["duration"]
            thumbnail = res["thumbnails"][0]["url"].split("?")[0]
            vidid = res["id"]
            if str(duration_min) == "None": duration_sec = 0
            else: duration_sec = int(time_to_seconds(duration_min))
            return title, duration_min, duration_sec, thumbnail, vidid
        except:
            pass

        # 2. Fallback: Use yt-dlp (Slower but 100% Works for ?si= links)
        print(f"⚠️ Search failed, trying yt-dlp fallback for: {link}")
        return await self.fallback_details(link)

    async def fallback_details(self, link):
        try:
            loop = asyncio.get_running_loop()
            opts = {"quiet": True, "no_warnings": True, "cookiefile": cookie_txt_file()}
            
            # ytsearch1: prefix handles both queries and links
            if not re.search(self.regex, link):
                link = f"ytsearch1:{link}"

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(link, download=False))
                
                if 'entries' in info: info = info['entries'][0] # Handle search results
                
                title = info.get("title")
                duration_sec = info.get("duration", 0)
                duration_min = str(int(duration_sec // 60)) + ":" + str(int(duration_sec % 60)).zfill(2)
                thumbnail = info.get("thumbnail")
                vidid = info.get("id")
                return title, duration_min, duration_sec, thumbnail, vidid
        except Exception as e:
            logger.error(f"❌ Fallback Failed: {e}")
            return None, None, None, None, None

    # 🔥 REWRITTEN: Track (Supports ?si= links)
    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        
        # Try finding via ID extraction first (Fastest for links)
        clean_id = self.extract_id(link)
        if clean_id:
            link = self.base + clean_id # Normalize URL

        try:
            results = VideosSearch(link, limit=1)
            res = (await results.next())["result"][0]
            title = res["title"]
            duration_min = res["duration"]
            vidid = res["id"]
            yturl = res["link"]
            thumbnail = res["thumbnails"][0]["url"].split("?")[0]
            return {"title": title, "link": yturl, "vidid": vidid, "duration_min": duration_min, "thumb": thumbnail}, vidid
        except:
            # Fallback to yt-dlp logic
            t, dm, ds, th, vi = await self.fallback_details(link)
            if t:
                return {"title": t, "link": self.base + vi, "vidid": vi, "duration_min": dm, "thumb": th}, vi
            return None, None

    async def title(self, link: str, videoid: Union[bool, str] = None):
        t, _, _, _, _ = await self.details(link, videoid)
        return t

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        _, d, _, _, _ = await self.details(link, videoid)
        return d

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        _, _, _, t, _ = await self.details(link, videoid)
        return t

    async def formats(self, link: str, videoid: Union[bool, str] = None): return [], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None,
    ) -> str:
        if videoid: link = self.base + link
        
        # Handle ?si= and other garbage in links before downloading
        clean_id = self.extract_id(link)
        if clean_id: link = self.base + clean_id

        # 1. API DOWNLOAD (Pass 'mystic' message object for Metadata)
        media_type = "video" if (video or songvideo) else "audio"
        try:
            # mystic is the Message object passed from the play command
            api_file = await download_via_api(link, media_type, message=mystic)
            if api_file: return api_file, True
        except Exception as e: 
            logger.error(f"API Download Logic Failed: {e}")

        # 2. LOCAL DOWNLOAD
        logger.info(f"⬇️ Starting Local Download: {link}")
        loop = asyncio.get_running_loop()
        cookies = cookie_txt_file()

        def local_dl(type_):
            opts = {
                "outtmpl": "downloads/%(id)s.%(ext)s", "geo_bypass": True, 
                "nocheckcertificate": True, "quiet": True, "no_warnings": True,
                "cookiefile": cookies
            }
            if type_ == "audio":
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
            else:
                opts["format"] = "bestvideo+bestaudio/best"; opts["merge_output_format"] = "mp4"
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=True)
                ext = "mp3" if type_ == "audio" else "mp4"
                return os.path.join("downloads", f"{info['id']}.{ext}")

        try:
            type_ = "video" if (video or songvideo) else "audio"
            fpath = await loop.run_in_executor(None, lambda: local_dl(type_))
            return fpath, True
        except Exception as e:
            logger.error(f"❌ Local Download Failed: {e}")
            return None, False
