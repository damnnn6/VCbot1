import json
import os
from os import path
from typing import Callable

import aiofiles
import aiohttp
import ffmpeg
import requests
import wget
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Voice
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import Message
from Python_ARQ import ARQ
from youtube_search import YoutubeSearch

from YuiHirasawaMusicBot.config import BOT_NAME
from YuiHirasawaMusicBot.config import BOT_USERNAME
from YuiHirasawaMusicBot.config import ASSISTANT_NAME
from YuiHirasawaMusicBot.config import ARQ_API_KEY
from YuiHirasawaMusicBot.config import DURATION_LIMIT
from YuiHirasawaMusicBot.config import UPDATES_CHANNEL as updateschannel
from YuiHirasawaMusicBot.config import que
from YuiHirasawaMusicBot.function.admins import admins as a
from YuiHirasawaMusicBot.helpers.admins import get_administrators
from YuiHirasawaMusicBot.helpers.channelmusic import get_chat_id
from YuiHirasawaMusicBot.helpers.errors import DurationLimitError
from YuiHirasawaMusicBot.helpers.decorators import errors
from YuiHirasawaMusicBot.helpers.decorators import authorized_users_only
from YuiHirasawaMusicBot.helpers.filters import command
from YuiHirasawaMusicBot.helpers.gets import get_file_name
from YuiHirasawaMusicBot.services.callsmusic import callsmusic
from YuiHirasawaMusicBot.services.callsmusic import client as USER
from YuiHirasawaMusicBot.services.converter.converter import convert
from YuiHirasawaMusicBot.services.downloaders import youtube
from YuiHirasawaMusicBot.services.queues import queues


aiohttpsession = aiohttp.ClientSession()
chat_id = None
arq = ARQ("https://thearq.tech", ARQ_API_KEY, aiohttpsession)
DISABLED_GROUPS = []
useer ="NaN"
def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes:
            return await func(client, cb)
        else:
            await cb.answer("لا يسمح لك!", show_alert=True)
            return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("./etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((205, 560), f"Title: {title}", (51, 215, 255), font=font)
    draw.text((205, 600), f"Duration: {duration}", (255, 255, 255), font=font)
    draw.text((205, 640), f"Views: {views}", (255, 255, 255), font=font)
    draw.text((205, 680), f"Added By: {requested_by}", (255, 255, 255), font=font)
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(command(["عرض القائمة","playlist",f"عرض القائمة@{BOT_USERNAME}",f"playlist@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot)
async def playlist(client, message):
    global que
    if message.chat.id in DISABLED_GROUPS:
        return    
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply_text("التشغيل متوقف ❍")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "**يشتغل الان** {}".format(message.chat.title)
    msg += "\n- " + now_playing
    msg += "\n- تم الطلب بوسطه " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**الدور**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n- {name}"
            msg += f"\n- تم الطلب بوسطه {usr}\n"
    await message.reply_text(msg)


# ============================= Settings =========================================


def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.active_chats:
        # if chat.id in active_chats:
        stats = "**{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "الصوت : {}%\n".format(vol)
            stats += "عدد الاغاني : `{}`\n".format(len(que))
            stats += "يشتغل الان : **{}**\n".format(queue[0][0])
            stats += "تم الطلب بوسطه : {}".format(queue[0][1].mention)
    else:
        stats = None
    return stats


def r_ply(type_):
    if type_ == "play":
        pass
    else:
        pass
    mar = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏹", "leave"),
                InlineKeyboardButton("⏸", "puse"),
                InlineKeyboardButton("▶️", "resume"),
                InlineKeyboardButton("⏭", "skip"),
            ],
            [
                InlineKeyboardButton("قائمة التشغيل 📖", "playlist"),
            ],
            [InlineKeyboardButton("❌ اغلاق", "cls")],
        ]
    )
    return mar


@Client.on_message(command(["المسار","current",f"المسار@{BOT_USERNAME}",f"current@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot)
async def ee(client, message):
    if message.chat.id in DISABLED_GROUPS:
        return
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("لا توجد اغاني قيد التشغيل ❍")


@Client.on_message(command(["التحكم","player",f"التحكم@{BOT_USERNAME}",f"player@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot)
@authorized_users_only
async def settings(client, message):
    if message.chat.id in DISABLED_GROUPS:
        await message.reply("مشغل الموسيقى معطل �")
        return    
    playing = None
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.active_chats:
        playing = True
    queue = que.get(chat_id)
    stats = updated_stats(message.chat, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause")) 
        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("لا توجد اغاني قيد التشغيل ❍")

@Client.on_message(command(["musicplayer","الموسيقي",f"الموسيقي@{BOT_USERNAME}",f"musicplayer@{BOT_USERNAME}"]) & ~filters.bot & ~filters.private)
@authorized_users_only
async def hfmm(_, message):
    global DISABLED_GROUPS
    try:
        user_id = message.from_user.id
    except:
        return
    if len(message.command) != 2:
        await message.reply_text(
            "اوامر التنشيط و التعطيل `/الموسيقي تنشيط` للتنشيط \n `/الموسيقي تعطيل` للتعطيل"
        )
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status == "ON" or status == "on" or status == "oN" or status == "On" or status == "تنشيط":
        lel = await message.reply("`معالجة...`")
        if not message.chat.id in DISABLED_GROUPS:
            await lel.edit("تم تنشيط مشغل الموسيقى بالفعل في هذه الدردشة ♢")
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"تم تمكين مشغل الموسيقى بنجاح للمستخدمين في الدردشة {message.chat.id}"
        )

    elif status == "OFF" or status == "OFf" or status == "Off" or status == "off" or status == "oFF" or status == "ofF" or status == "OfF" or status == "oFf" or status == "تعطيل":
        lel = await message.reply("`معالجة...`")
        
        if message.chat.id in DISABLED_GROUPS:
            await lel.edit("تم إيقاف تشغيل مشغل الموسيقى بالفعل في هذه الدردشة ♢")
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"تم إلغاء تنشيط مشغل الموسيقى بنجاح للمستخدمين في الدردشة {message.chat.id}"
        )
    else:
        await message.reply_text(
            "اوامر التنشيط و التعطيل `/musicplayer on` للتنشيط \n `/musicplayer off` للتعطيل"
        )    
        

@Client.on_callback_query(filters.regex(pattern=r"^(playlist)$"))
async def p_cb(b, cb):
    global que
    que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("المشغل في وضع الايقاف ☹")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "<b>تشغيل الان</b> in {}".format(cb.message.chat.title)
        msg += "\n- " + now_playing
        msg += "\n- Req by " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Queue**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- Req by {usr}\n"
        await cb.message.edit(msg)


@Client.on_callback_query(
    filters.regex(pattern=r"^(play|pause|skip|leave|puse|resume|menu|cls)$")
)
@cb_admin_check
async def m_cb(b, cb):
    global que
    if (
        cb.message.chat.title.startswith("Channel Music: ")
        and chat.title[14:].isnumeric()
    ):
        chet_id = int(chat.title[13:])
    else:
        chet_id = cb.message.chat.id
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat

    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "pause":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "paused"
        ):
            await cb.answer("المحادثه غير متصلة!", show_alert=True)
        else:
            callsmusic.pause(chet_id)
            await cb.answer("Music Paused!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("play")
            )

    elif type_ == "play":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "playing"
        ):
            await cb.answer("المحادثه غير متصلة!", show_alert=True)
        else:
            callsmusic.resume(chet_id)
            await cb.answer("Music Resumed!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Player is idle")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**Now Playing** in {}".format(cb.message.chat.title)
        msg += "\n- " + now_playing
        msg += "\n- Req by " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Queue**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- Req by {usr}\n"
        await cb.message.edit(msg)

    elif type_ == "resume":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "playing"
        ):
            await cb.answer("المحادثه غير متصلة أو يعمل بالفعل", show_alert=True)
        else:
            callsmusic.resume(chet_id)
            await cb.answer("Music Resumed!")
    elif type_ == "puse":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "paused"
        ):
            await cb.answer("المحادثه غير متصلة او تم الايقاف مؤقتا بلفعل", show_alert=True)
        else:
            callsmusic.pause(chet_id)
            await cb.answer("Music Paused!")
    elif type_ == "cls":
        await cb.answer("Closed menu")
        await cb.message.delete()

    elif type_ == "menu":
        stats = updated_stats(cb.message.chat, qeue)
        await cb.answer("Menu opened")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏹", "leave"),
                    InlineKeyboardButton("⏸", "puse"),
                    InlineKeyboardButton("▶️", "resume"),
                    InlineKeyboardButton("⏭", "skip"),
                ],
                [
                    InlineKeyboardButton("Playlist 📖", "playlist"),
                ],
                [InlineKeyboardButton("❌ اغلاق", "cls")],
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)
    elif type_ == "skip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.active_chats:
            await cb.answer("المحادثه غير متصلة!", show_alert=True)
        else:
            queues.task_done(chet_id)
            if queues.is_empty(chet_id):
                callsmusic.stop(chet_id)
                await cb.message.edit("- No More Playlist..\n- Leaving VC!")
            else:
                await callsmusic.set_stream(
                    chet_id, queues.get(chet_id)["file"]
                )
                await cb.answer.reply_text("✅ <b>تم التخطي</b>")
                await cb.message.edit((m_chat, qeue), reply_markup=r_ply(the_data))
                await cb.message.reply_text(
                    f"- تم التخطي\n- يشتغل الان **{qeue[0][0]}**"
                )

    else:
        if chet_id in callsmusic.active_chats:
            try:
               queues.clear(chet_id)
            except QueueEmpty:
                pass

            await callsmusic.stop(chet_id)
            await cb.message.edit("نجح في مغادرة الدردشة!")
        else:
            await cb.answer("الدردشة غير متصلة!", show_alert=True)


@Client.on_message(command(["play","تشغيل",f"تشغيل@{BOT_USERNAME}",f"play@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot)
async def play(_, message: Message):
    global que
    global useer
    if message.chat.id in DISABLED_GROUPS:
        return    
    lel = await message.reply("🔄 <b>معالجة</b>")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "helper"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>تذكر أن تضيف المساعد إلى قناتك</b>",
                    )
                    pass
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>أضفني كمسؤول في مجموعتك أولاً ☺</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "انضممت إلى هذه المجموعة لتشغيل الموسيقى ☻"
                    )
                    await lel.edit(
                        f"<b>انضم الحساب المساعد @{ASSISTANT_NAME} إلى محادثتك</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>هناك خطاء �</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> الحساب المساعد ليس في هذه الدردشة ، اطلب من المسؤول إرسال `/انضم` لأول مرة أو الإضافة @{ASSISTANT_NAME} يدويا</i>"
        )
        return
    text_links=None
    await lel.edit("🔎<b>يتم التشغيل\nفي حالة لم تشتغل قم بي مسح اي رابط او ماركداون في وصف الاغنية\nيستحسن مسح الوصف كامل</b>")
    if message.reply_to_message:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            pass
        entities = []
        toxt =  message.reply_to_message.text \
              or message.reply_to_message.caption
        if message.reply_to_message.entities:
            entities = message.reply_to_message.entities + entities
        elif message.reply_to_message.caption_entities:
            entities = message.reply_to_message.entities + entities
        urls = [entity for entity in entities if entity.type == 'url']
        text_links = [
            entity for entity in entities if entity.type == 'text_link'
        ]
    else:
        urls=None
    if text_links:
        urls = True
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ مقاطع الفيديو أطول من {DURATION_LIMIT} دقيقة غير مسموح لها بالتشغيل !"
            )
            return
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="playlist"),
                    InlineKeyboardButton("قائمة ⏯ ", callback_data="menu"),
                ],
                [
                    InlineKeyboardButton(text="❌ اغلاق", callback_data="cls")
                ],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/f6086f8909fbfeb0844f2.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "ERROR"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("🎵 <b>معالجة</b>")
        ydl_opts = {"format": "bestaudi[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "لم يتم العثور على الأغنية ، جرب أغنية أخرى أو ربما تهجئها بشكل صحيح √."
            )
            print(str(e))
            return
        try:    
            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 60
            if (dur / 60) > DURATION_LIMIT:
                 await lel.edit(f"❌ الاغنيه أطول من {DURATION_LIMIT} دقيقة غير مسموح لي بالتشغيل ")
                 return
        except:
            pass        
        dlurl=url
        dlurl=dlurl.replace("youtube","youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="playlist"),
                    InlineKeyboardButton("قائمة ⏯ ", callback_data="menu"),
                ],
                [
                    InlineKeyboardButton(text="❌ اغلاق", callback_data="cls")
                ],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))        
    else:
        query = ""
        for i in message.command[1:]:
            query += " " + str(i)
        print(query)
        await lel.edit("🎵 **معالجة**")
        ydl_opts = {"format": "bestaudi[ext=m4a]"}
        
        try:
          results = YoutubeSearch(query, max_results=5).to_dict()
        except:
          await lel.edit("ارسل شيئ للتشغيل ♦")
        # Looks like hell. Aren't it?? FUCK OFF
        try:
            toxxt = "**حدد الأغنية التي تريد تشغيلها**\n\n"
            j = 0
            useer=user_name
            emojilist = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣",]

            while j < 5:
                toxxt += f"{emojilist[j]} <b>Title - [{results[j]['title']}](https://youtube.com{results[j]['url_suffix']})</b>\n"
                toxxt += f" ╚ <b>المدة</b> - {results[j]['duration']}\n"
                toxxt += f" ╚ <b>المشاهدات</b> - {results[j]['views']}\n"
                toxxt += f" ╚ <b>القناة</b> - {results[j]['channel']}\n\n"
                toxxt += f" <b>يمكنك الضغط علي الازرار في الاسفل لي تشغيل الاغنيه</b>"
                
                j += 1            
            koyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("1️⃣", callback_data=f'plll 0|{query}|{user_id}'),
                        InlineKeyboardButton("2️⃣", callback_data=f'plll 1|{query}|{user_id}'),
                        InlineKeyboardButton("3️⃣", callback_data=f'plll 2|{query}|{user_id}'),
                    ],
                    [
                        InlineKeyboardButton("4️⃣", callback_data=f'plll 3|{query}|{user_id}'),
                        InlineKeyboardButton("5️⃣", callback_data=f'plll 4|{query}|{user_id}'),
                    ],
                    
                    [InlineKeyboardButton(text="❌", callback_data="cls")],
                ]
            )       
            await lel.edit(toxxt,reply_markup=koyboard,disable_web_page_preview=True)
            # WHY PEOPLE ALWAYS LOVE PORN ?? (A point to think)
            return
            # Returning to pornhub
        except:
            await lel.edit("لا توجد نتائج كافية للاختيار .. بدء التشغيل المباشر..")
                        
            # print(results)
            try:
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:40]
                thumbnail = results[0]["thumbnails"][0]
                thumb_name = f"thumb{title}.jpg"
                thumb = requests.get(thumbnail, allow_redirects=True)
                open(thumb_name, "wb").write(thumb.content)
                duration = results[0]["duration"]
                results[0]["url_suffix"]
                views = results[0]["views"]

            except Exception as e:
                await lel.edit(
                    "لم يتم العثور على الأغنية ، جرب أغنية أخرى أو ربما تهجئها بشكل صحيح."
                )
                print(str(e))
                return
            try:    
                secmul, dur, dur_arr = 1, 0, duration.split(':')
                for i in range(len(dur_arr)-1, -1, -1):
                    dur += (int(dur_arr[i]) * secmul)
                    secmul *= 60
                if (dur / 60) > DURATION_LIMIT:
                     await lel.edit(f"❌ مقاطع الفيديو أطول من {DURATION_LIMIT} دقيقة (دقائق) غير مسموح لها بالتشغيل ")
                     return
            except:
                pass
            dlurl=url
            dlurl=dlurl.replace("youtube","youtubepp")
            keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="playlist"),
                    InlineKeyboardButton("قائمة ⏯ ", callback_data="menu"),
                ],
                [
                    InlineKeyboardButton(text="❌ اغلاق", callback_data="cls")
                ],
            ]
        )
            requested_by = message.from_user.first_name
            await generate_cover(requested_by, title, views, duration, thumbnail)
            file_path = await convert(youtube.download(url))   
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.active_chats:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption=f"#⃣ الأغنية التي طلبتها <b>queued</b> في المنصة {position}!",
            reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            await callsmusic.set_stream(chat_id, file_path)
        except:
            message.reply("المكالمة الجماعية غير متصلة أو لا يمكنني الانضمام إليها")
            return
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="▶️ <b>يشغل</b> هنا الأغنية التي طلبها {}".format(
                message.from_user.mention()
            ),
        )
        os.remove("final.png")
        return await lel.delete()


@Client.on_message(command(["ytplay","يوتيوب تشغيل",f"ytplay@{BOT_USERNAME}",f"يوتيوب تشغيل@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot)
async def ytplay(_, message: Message):
    global que
    if message.chat.id in DISABLED_GROUPS:
        return
    lel = await message.reply("🔄 <b>معالجة</b>")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "helper"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>تذكر أن تضيف الحساب المساعد إلى قناتك</b>",
                    )
                    pass
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>أضفني كمسؤول في مجموعتك أولاً</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "انضممت إلى هذه المجموعة لتشغيل الموسيقى"
                    )
                    await lel.edit(
                        "<b>انضم الحساب المساعد إلى محادثتك</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 خطأ هناك ضغط علي الحساب المساعد 🔴 \n لا يمكن الانضمام إلى مجموعتك بسبب الطلبات الكثيفة على الحساب المساعد! تأكد من عدم حظر الحساب المساعد @{ASSISTANT_NAME} في المجموعة."
                        f"\n\nأو أضف الحساب المساعد @{ASSISTANT_NAME} يدويًا إلى مجموعتك وحاول مرة أخرى</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>الحساب المساعد ليس في هذه الدردشة ، اطلب من المسؤول الإرسال `/انضم` او اضف البوت يدويا @{ASSISTANT_NAME}</i>"
        )
        return
    await lel.edit("🔎 <b>يبحث</b>")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
     

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    await lel.edit("🎵 <b>معالجه</b>")
    ydl_opts = {"format": "bestaudi[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        results[0]["url_suffix"]
        views = results[0]["views"]

    except Exception as e:
        await lel.edit(
            "لم يتم العثور على الأغنية ، جرب أغنية أخرى أو ربما تهجئها بشكل صحيح."
        )
        print(str(e))
        return
    try:    
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
             await lel.edit(f"❌ مده الفيديو تتخطي {DURATION_LIMIT} دقيقة لا يمكنني تشغيله!")
             return
    except:
        pass    
    dlurl=url
    dlurl=dlurl.replace("youtube","youtubepp")
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="playlist"),
                    InlineKeyboardButton("قائمة ⏯ ", callback_data="menu"),
                ],
                [
                    InlineKeyboardButton(text="❌ اغلاق", callback_data="cls")
                ],
            ]
        )
    requested_by = message.from_user.first_name
    await generate_cover(requested_by, title, views, duration, thumbnail)
    file_path = await convert(youtube.download(url))
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.active_chats:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption=f"#⃣ الأغنية التي طلبتها <b>في قائمة الانتظار</b> في الموضع {position}!",
            reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
           await callsmusic.set_stream(chat_id, file_path)
        except:
            message.reply("المكالمة الجماعية غير متصلة أو لا يمكنني الانضمام إليها")
            return
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="▶️ <b>يشتغل</b> هنا الأغنية التي طلبتها {} ".format(
                message.from_user.mention()
            ),
        )
        os.remove("final.png")
        return await lel.delete()
    
@Client.on_message(command(["dplay","ديزر تشغيل",f"dplay@{BOT_USERNAME}",f"ديزر تشغيل@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot)
async def deezer(client: Client, message_: Message):
    if message_.chat.id in DISABLED_GROUPS:
        return
    global que
    lel = await message_.reply("🔄 <b>معالجه</b>")
    administrators = await get_administrators(message_.chat)
    chid = message_.chat.id
    try:
        user = await USER.get_me()
    except:
        user.first_name = "DaisyMusic"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>تذكر أن تضيف الحساب المساعد إلى قناتك</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>أضفني كمسؤول في مجموعتك أولاً</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message_.chat.id, "انضممت إلى هذه المجموعة لتشغيل الموسيقى"
                    )
                    await lel.edit(
                        "<b>انضم الحساب المساعد إلى محادثتك</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 خطأ هناك ضغط علي الحساب المساعد 🔴 \n لا يمكن الانضمام إلى مجموعتك بسبب الطلبات الكثيفة على الحساب المساعد! تأكد من عدم حظر الحساب المساعد @{ASSISTANT_NAME} في المجموعة."
                        f"\n\nأو أضف الحساب المساعد @{ASSISTANT_NAME} يدويًا إلى مجموعتك وحاول مرة أخرى</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>الحساب المساعد ليس في هذه الدردشة ، اطلب من المسؤول الإرسال `/انضم` او اضف البوت يدويا @{ASSISTANT_NAME}</i>"
        )
        return
    requested_by = message_.from_user.first_name

    text = message_.text.split(" ", 1)
    queryy = text[1]
    query = queryy
    res = lel
    await res.edit(f"🔍 يتم البحث عن `{queryy}` علي ديزر")
    try:
        songs = await arq.deezer(query,1)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        title = songs.result[0].title
        url = songs.result[0].url
        artist = songs.result[0].artist
        duration = songs.result[0].duration
        thumbnail = "https://telegra.ph/file/f6086f8909fbfeb0844f2.png"

    except:
        await res.edit("لم يتم العثور على أي شيء حرفيًا ، يجب أن تعمل على تحسين مستواك في اللغة الإنجليزية!")
        return
    try:    
        duuration= round(duration / 60)
        if duuration > DURATION_LIMIT:
            await cb.message.edit(f"الموسيقي اطول من {DURATION_LIMIT} دقيقة لا يمكنني البدء")
            return
    except:
        pass    
    
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="playlist"),
                    InlineKeyboardButton("قائمة ⏯ ", callback_data="menu"),
                ],
                [
                    InlineKeyboardButton(text="❌ اغلاق", callback_data="cls")
                ],
            ]
        )
    file_path = await convert(wget.download(url))
    await res.edit("Generating Thumbnail")
    await generate_cover(requested_by, title, artist, duration, thumbnail)
    chat_id = get_chat_id(message_.chat)
    if chat_id in callsmusic.active_chats:
        await res.edit("adding in queue")
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.edit_text(f"✯{bn}✯= #️⃣ في قائمة الانتظار {position}")
    else:
        await res.edit_text(f"✯{bn}✯=▶️ يشتغل.....")

        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            await callsmusic.set_stream(chat_id, file_path)
        except:
            res.edit("المكالمة الجماعية غير متصلة لأنني لا أستطيع الانضمام إليها")
            return

    await res.delete()

    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"يشتغل [{title}]({url}) عبر ديزر",
    )
    os.remove("final.png")


@Client.on_message(command("splay") & ~filters.private & ~filters.bot)
async def jiosaavn(client: Client, message_: Message):
    global que
    if message_.chat.id in DISABLED_GROUPS:
        return    
    lel = await message_.reply("🔄 <b>معالجه</b>")
    administrators = await get_administrators(message_.chat)
    chid = message_.chat.id
    try:
        user = await USER.get_me()
    except:
        user.first_name = "DaisyMusic"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>تذكر أن تضيف الحساب المساعد إلى قناتك</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>أضفني كمسؤول عن مجموعتك أولاً</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message_.chat.id, "انضممت إلى هذه المجموعة لتشغيل الموسيقى في VC"
                    )
                    await lel.edit(
                        "<b>انضم الحساب المساعد إلى محادثتك</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 خطأ يوجد ضغط علي الحساب المساعد 🔴 \nالمستخدم {user.first_name} لا يمكن الانضمام إلى مجموعتك بسبب الطلبات الكثيفة على الحساب المساعد تأكد من عدم حظر المستخدم في المجموعة."
                        f"\n\nأو أضف يدويًا @{ASSISTANT_NAME} إلى مجموعتك وحاول مرة أخرى</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            "<i> الحساب مساعد ليس في هذه الدردشة ، اطلب من المسؤول الإرسال \n /انضم او /تشغيل \n لأول مرة أو إضافة الحساب المساعد يدويًا</i>"
        )
        return
    requested_by = message_.from_user.first_name + " " + message_.from_user.last_name
    chat_id = message_.chat.id
    text = message_.text.split(" ", 1)
    query = text[1]
    res = lel
    await res.edit(f"يبحث 🔍 عن `{query}` ")
    try:
        songs = await arq.saavn(query)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        sname = songs.result[0].song
        slink = songs.result[0].media_url
        ssingers = songs.result[0].singers
        sthumb = songs.result[0].image
        sduration = int(songs.result[0].duration)
    except Exception as e:
        await res.edit("لم يتم العثور على أي شيء حرفيًا! ، يجب أن تعمل على تحسين مستواك في اللغة الإنجليزية.")
        print(str(e))
        return
    try:    
        duuration= round(sduration / 60)
        if duuration > DURATION_LIMIT:
            await cb.message.edit(f"الموسيقى أطول من {DURATION_LIMIT} دقيقة لا يمكنني تشغيلها")
            return
    except:
        pass    
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="playlist"),
                    InlineKeyboardButton("قائمة ⏯ ", callback_data="menu"),
                ],
                [
                    InlineKeyboardButton(text="❌ اغلاق", callback_data="cls")
                ],
            ]
        )
    file_path = await convert(wget.download(slink))
    chat_id = get_chat_id(message_.chat)
    if chat_id in callsmusic.active_chats:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = sname
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.delete()
        m = await client.send_photo(
            chat_id=message_.chat.id,
            reply_markup=keyboard,
            photo="final.png",
            caption=f"✯{bn}✯=#️⃣ في قائمة الانتظار {position}",
        )

    else:
        await res.edit_text(f"{bn}=▶️ يشتغل.....")
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = sname
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            await callsmusic.set_stream(chat_id, file_path)
        except:
            res.edit("المكالمة الجماعية غير متصلة لا أستطيع الانضمام إليها")
            return
    await res.edit("توليد الصورة المصغرة.")
    await generate_cover(requested_by, sname, ssingers, sduration, sthumb)
    await res.delete()
    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"يشتغل {sname} ",
    )
    os.remove("final.png")


@Client.on_callback_query(filters.regex(pattern=r"plll"))
async def lol_cb(b, cb):
    global que

    cbd = cb.data.strip()
    chat_id = cb.message.chat.id
    typed_=cbd.split(None, 1)[1]
    #useer_id = cb.message.reply_to_message.from_user.id
    try:
        x,query,useer_id = typed_.split("|")      
    except:
        await cb.message.edit("لم يتم العثور على الاغنية")
        return
    useer_id = int(useer_id)
    if cb.from_user.id != useer_id:
        await cb.answer("أنت لست الشخص الذي طلب تشغيل الأغنية!", show_alert=True)
        return
    await cb.message.edit("انتظر  لحظة للتشغيل ☻")
    x=int(x)
    try:
        useer_name = cb.message.reply_to_message.from_user.first_name
    except:
        useer_name = cb.message.from_user.first_name
    
    results = YoutubeSearch(query, max_results=5).to_dict()
    resultss=results[x]["url_suffix"]
    title=results[x]["title"][:40]
    thumbnail=results[x]["thumbnails"][0]
    duration=results[x]["duration"]
    views=results[x]["views"]
    url = f"https://youtube.com{resultss}"
    
    try:    
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
             await cb.message.edit(f"الموسيقى أطول من {DURATION_LIMIT} دقيقة لايمكن تشغيلها")
             return
    except:
        pass
    try:
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
    except Exception as e:
        print(e)
        return
    dlurl=url
    dlurl=dlurl.replace("youtube","youtubepp")
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="playlist"),
                    InlineKeyboardButton("قائمة ⏯ ", callback_data="menu"),
                ],
                [
                    InlineKeyboardButton(text="❌ اغلاق", callback_data="cls")
                ],
            ]
        )
    requested_by = useer_name
    await generate_cover(requested_by, title, views, duration, thumbnail)
    file_path = await convert(youtube.download(url))  
    if chat_id in callsmusic.active_chats:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        try:
            r_by = cb.message.reply_to_message.from_user
        except:
            r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await cb.message.delete()
        await b.send_photo(chat_id,
            photo="final.png",
            caption=f"#⃣ تم طلب الأغنية بواسطة {r_by.mention} <b>في قائمة الانتظار</b> في الانتظار {position}!",
            reply_markup=keyboard,
        )
        os.remove("final.png")
        
    else:
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        try:
            r_by = cb.message.reply_to_message.from_user
        except:
            r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
    
        await callsmusic.set_stream(chat_id, file_path)
        await cb.message.delete()
        await b.send_photo(chat_id,
            photo="final.png",
            reply_markup=keyboard,
            caption=f"▶️ <b>يشتغل</b> هنا الأغنية التي طلبتها {r_by.mention} عبر يوتيوب 😎",
        )
        
        os.remove("final.png")
