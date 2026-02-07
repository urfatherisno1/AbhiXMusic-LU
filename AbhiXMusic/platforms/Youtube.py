import asyncio
import os
import re
import json
import glob
import random
import logging
import time
import aiohttp
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from AbhiXMusic.utils.database import is_on_off
from AbhiXMusic.utils.formatters import time_to_seconds
from config import API_URL, API_KEY

# 🔥 BEAUTIFUL LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)
logger = logging.getLogger("Youtube")

HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

def cookie_txt_file():
    folder_path = f"{os.getcwd()}/cookies"
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files: return None
    return random.choice(txt_files)

async def download_via_api(link: str, media_type: str, message: Message = None):
    if not API_URL: return None
    
    start_time = time.time()
    requester = "Unknown"
    chat_title = "Private"

    payload = {"url": link, "type": media_type, "quality": "best"}
    if message:
        try:
            chat = message.chat
            user = message.from_user
            chat_title = chat.title or "Private"
            requester = user.first_name if user else "Unknown"
            payload.update({
                "chat_id": chat.id,
                "chat_title": chat_title,
                "requester_name": requester,
            })
        except: pass

    logger.info(f"📡 [API REQUEST] | 👤 {requester} | 🏘 {chat_title} | 🔗 {link}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload, headers=HEADERS, timeout=120) as resp:
                elapsed = time.time() - start_time
                if resp.status == 200:
                    data = await resp.json()
                    file_path = data.get("file")
                    if file_path:
                        filename = os.path.basename(file_path)
                        base_url = API_URL.replace("/download", "")
                        stream_url = f"{base_url}/stream/{filename}"
                        
                        # 🔥 DETAILED SUCCESS LOG
                        logger.info(f"✅ [API SUCCESS] | 🎵 {filename} | ⏱ {elapsed:.2f}s | 🔗 {stream_url}")
                        return stream_url
                else:
                    logger.error(f"❌ [API FAILED] | Status: {resp.status} | Time: {elapsed:.2f}s")
        except Exception as e:
            logger.error(f"❌ [API ERROR] Connection Failed: {e}")
    return None

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

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
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
        except: return "Unknown", "0:00", 0, "", ""

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
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
            logger.info(f"⚠️ Track Fallback: Using yt-dlp (iOS) for {link}")
            try:
                loop = asyncio.get_running_loop()
                opts = {
                    "quiet": True, 
                    "cookiefile": cookie_txt_file(), 
                    "noplaylist": True,
                    "extractor_args": {"youtube": {"player_client": ["ios"]}}
                }
                
                if "http" not in link: search_query = f"ytsearch1:{link}"
                else: search_query = link

                def get_info():
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        return ydl.extract_info(search_query, download=False)

                info = await loop.run_in_executor(None, get_info)
                if 'entries' in info: info = info['entries'][0]

                title = info.get("title")
                vidid = info.get("id")
                yturl = f"https://www.youtube.com/watch?v={vidid}"
                duration_sec = info.get("duration", 0)
                duration_min = f"{duration_sec // 60}:{duration_sec % 60:02d}"
                thumbnail = info.get("thumbnail")
                
                return {"title": title, "link": yturl, "vidid": vidid, "duration_min": duration_min, "thumb": thumbnail}, vidid
            except Exception as e:
                logger.error(f"❌ Track Failed: {e}")
                return {"title": "Unknown Song", "link": link, "vidid": "", "duration_min": "0:00", "thumb": ""}, ""

    async def formats(self, link: str, videoid: Union[bool, str] = None): return [], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        result = (await VideosSearch(link, limit=10).next()).get("result")
        return result[query_type]["title"], result[query_type]["duration"], result[query_type]["thumbnails"][0]["url"].split("?")[0], result[query_type]["id"]

    async def download(
        self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None,
    ) -> str:
        
        start_dl_time = time.time()
        original_query = link
        if videoid: link = self.base + link

        # 🛑 BLOCK GHOST LINKS
        if link.strip() == "https://www.youtube.com/watch?v=" or link.endswith("watch?v="):
            logger.warning("👻 Ghost Link Detected!")
            if title and title != "Unknown":
                link = title
                logger.info(f"🔄 Switching to Title Search: {link}")
            elif original_query and "http" not in original_query:
                link = original_query
                logger.info(f"🔄 Switching to Original Query: {link}")
            else:
                logger.error("🚫 ABORT: Empty Link & No Title.")
                return None, False

        # 2. SEARCH LOGIC
        if "youtube.com" not in link and "youtu.be" not in link:
            try:
                results = VideosSearch(link, limit=1)
                res = (await results.next())["result"][0]
                link = res["link"]
                logger.info(f"🔍 Resolved Query: {original_query} -> {link}")
            except: pass 

        # 3. API DOWNLOAD
        media_type = "video" if (video or songvideo) else "audio"
        try:
            if "watch?v=" in link and len(link) > 30:
                api_file = await download_via_api(link, media_type, message=mystic)
                if api_file: return api_file, True
        except: pass

        # 4. LOCAL DOWNLOAD
        logger.info(f"⬇️ Local Fallback: {link}")
        loop = asyncio.get_running_loop()
        cookies = cookie_txt_file()

        def local_dl(type_):
            opts = {
                "outtmpl": "downloads/%(id)s.%(ext)s", 
                "geo_bypass": True, 
                "nocheckcertificate": True, 
                "quiet": True, 
                "no_warnings": True,
                "cookiefile": cookies,
                "extractor_args": {"youtube": {"player_client": ["ios"]}}
            }
            if type_ == "audio":
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
            else:
                opts["format"] = "bestvideo+bestaudio/best"
                opts["merge_output_format"] = "mp4"
            
            dl_link = link
            if "youtube.com" not in dl_link and "youtu.be" not in dl_link:
                dl_link = f"ytsearch1:{dl_link}"

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(dl_link, download=True)
                if 'entries' in info: info = info['entries'][0]
                ext = "mp3" if type_ == "audio" else "mp4"
                return os.path.join("downloads", f"{info['id']}.{ext}")

        try:
            type_ = "video" if (video or songvideo) else "audio"
            fpath = await loop.run_in_executor(None, lambda: local_dl(type_))
            
            # 🔥 LOCAL SUCCESS LOG
            if fpath and os.path.exists(fpath):
                file_size = os.path.getsize(fpath) / (1024 * 1024)
                elapsed = time.time() - start_dl_time
                logger.info(f"✅ [LOCAL SUCCESS] | 🎵 {os.path.basename(fpath)} | 📦 {file_size:.2f} MB | ⏱ {elapsed:.2f}s")
                return fpath, True
                
        except Exception as e:
            logger.error(f"❌ Local Download Failed: {e}")
            return None, False
