import aiohttp
import json
import sys
from pyrogram import filters, Client
from youtube_dl import YoutubeDL
from __future__ import unicode_literals
import asyncio
import math
import os
import time
from random import randint
from urllib.parse import urlparse
import aiofiles
import aiohttp
import requests
import wget
import youtube_dl
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from YuiHirasawaMusicBot.config import BOT_USERNAME
from YuiHirasawaMusicBot.config import DURATION_LIMIT
from YuiHirasawaMusicBot.modules.play import arq


from youtube_dl.utils import (
    ContentTooShortError,
    DownloadError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

@Client.on_message(filters.command(["song",f"song@{BOT_USERNAME}","تحميل","تحميل@{BOT_USERNAME}"]) & ~filters.edited)
async def song(client, message):
    cap = f"@{BOT_USERNAME}"
    url = message.text.split(None, 1)[1]
    rkp = await message.reply("معالجه...")
    if not url:
        await rkp.edit("**لي تحميل اغنيه?**\nاكتب`/تحميل` <اسم الاغنيه>")
    search = SearchVideos(url, offset=1, mode="json", max_results=1)
    test = search.result()
    p = json.loads(test)
    q = p.get("search_result")
    try:
        url = q[0]["link"]
    except BaseException:
        return await rkp.edit("فشل في العثور على تلك الأغنية.")
    type = "audio"
    if type == "audio":
        opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        song = True
    try:
        await rkp.edit("جاري التحميل...")
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except DownloadError as DE:
        await rkp.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await rkp.edit("`كان محتوى التنزيل قصيرًا جدًا.`")
        return
    except GeoRestrictedError:
        await rkp.edit(
            "`الفيديو غير متاح من موقعك الجغرافي بسبب القيود الجغرافية التي يفرضها موقع الويب.`"
        )
        return
    except MaxDownloadsReached:
        await rkp.edit("`تم الوصول إلى الحد الأقصى لعدد التنزيلات.`")
        return
    except PostProcessingError:
        await rkp.edit("`كان هناك خطأ أثناء معالجة ما بعد.`")
        return
    except UnavailableVideoError:
        await rkp.edit("`الوسائط غير متوفرة بالتنسيق المطلوب.`")
        return
    except XAttrMetadataError as XAME:
        await rkp.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await rkp.edit("`حدث خطأ أثناء استخراج المعلومات.`")
        return
    except Exception as e:
        await rkp.edit(f"{str(type(e)): {str(e)}}")
        return
    time.time()
    if song:
        await rkp.edit("جاري الرفع...") #blaze
        lel = await message.reply_audio(
                 f"{rip_data['id']}.mp3",
                 duration=int(rip_data["duration"]),
                 title=str(rip_data["title"]),
                 performer=str(rip_data["uploader"]),
                 caption=cap)  #JEcode
        await rkp.delete()
