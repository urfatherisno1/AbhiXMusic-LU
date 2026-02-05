import asyncio
import os
import re
import json
import random
import logging
import aiohttp
import subprocess
import glob  # 🔥 Yeh missing tha tere snippet mein
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from AbhiXMusic.utils.database import is_on_off
from AbhiXMusic.utils.formatters import time_to_seconds
from config import API_URL, API_KEY

logging.basicConfig(level=logging.INFO)
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
    if "youtube.com" not in link and "youtu.be" not in link: 
        link = f"https://www.youtube.com/watch?v={link}"

    payload = {"url": link, "type": media_type, "quality": "best"}
    
    if message:
        try:
            chat = message.chat; user = message.from_user
            payload.update({
                "chat_id": chat.id, 
                "chat_title": chat.title or "Private", 
                "chat_link": f"https://t.me/{chat.username}" if chat.username else "Private",
                "requester_id": user.id if user else 0, 
                "requester_name": user.first_name if user else "Unknown",
                "requester_username": user.username if user else "None"
            })
        except: pass

    # 📡 TERMINAL DEBUG LOGS
    print(f"\n📡 [API REQUEST] | TYPE: {media_type.upper()} | URL: {link}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload, headers=HEADERS, timeout=180) as resp:
                print(f"📥 [API RESPONSE] | STATUS: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    file_path = data.get("file")
                    if not file_path: 
                        print("❌ [API ERROR] | No file path returned")
                        return None
                    
                    filename = os.path.basename(file_path)
                    base_url = API_URL.replace("/download", "")
                    stream_url = f"{base_url}/stream/{filename}"
                    print(f"✅ [API SUCCESS] | STREAM URL: {stream_url}")
                    return stream_url
                else:
                    print(f"❌ [API FAILED] | ERROR: {await resp.text()}")
        except Exception as e: 
            print(f"❌ [API CONNECTION ERROR] | {str(e)}")
    return None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

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
        except: return None, None

    async def download(self, link, mystic, video=False, **kwargs):
        # 🔥 FIXED vplay logic: Don't let variables be unbound
        songvideo = kwargs.get("songvideo")
        is_video = bool(video or songvideo)
        m_type = "video" if is_video else "audio"

        # 1. TRY API STREAM FIRST
        api_url = await download_via_api(link, m_type, mystic)
        if api_url: return api_url, True

        # 2. LOCAL FALLBACK
        logger.info(f"⬇️ Local Fallback (API Failed): {link}")
        loop = asyncio.get_running_loop()
        cookies = cookie_txt_file()
        
        def local_dl_cli():
            # Check is_video here for correct format
            fmt = ["-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3"] if not is_video else ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]
            try:
                id_cmd = ["yt-dlp", "--js-runtimes", "node", "--get-id", "--", link]
                if cookies: id_cmd.insert(1, f"--cookies={cookies}")
                vid_id = subprocess.check_output(id_cmd).decode().strip()
                
                outtmpl = "downloads/%(title)s.%(ext)s"
                cmd = ["yt-dlp", "--js-runtimes", "node", "--remote-components", "ejs:github", "--no-warnings", "--geo-bypass", "--force-ipv4", "-o", outtmpl] + fmt
                if cookies: cmd.extend(["--cookies", cookies])
                cmd.append("--"); cmd.append(link)
                
                name_cmd = ["yt-dlp", "--get-filename", "-o", outtmpl, "--", link]
                if cookies: name_cmd.insert(1, f"--cookies={cookies}")
                fpath = subprocess.check_output(name_cmd).decode().strip()
                
                subprocess.run(cmd, check=True)
                return fpath
            except: return None

        fpath = await loop.run_in_executor(None, local_dl_cli)
        if fpath and os.path.exists(fpath): return fpath, True
        return None, False

    async def title(self, link: str, videoid: Union[bool, str] = None): return (await self.details(link, videoid))[0]
    async def duration(self, link: str, videoid: Union[bool, str] = None): return (await self.details(link, videoid))[1]
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None): return (await self.details(link, videoid))[3]
    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        result = (await VideosSearch(link, limit=10).next()).get("result")
        return result[query_type]["title"], result[query_type]["duration"], result[query_type]["thumbnails"][0]["url"].split("?")[0], result[query_type]["id"]
    async def formats(self, link: str, videoid: Union[bool, str] = None): return [], link
