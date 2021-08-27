
import json
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
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import Voice
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Python_ARQ import ARQ
from youtube_search import YoutubeSearch
from YuiHirasawaMusicBot.modules.play import generate_cover
from YuiHirasawaMusicBot.modules.play import arq
from YuiHirasawaMusicBot.modules.play import cb_admin_check
from YuiHirasawaMusicBot.modules.play import transcode
from YuiHirasawaMusicBot.modules.play import convert_seconds
from YuiHirasawaMusicBot.modules.play import time_to_seconds
from YuiHirasawaMusicBot.modules.play import changeImageSize
from YuiHirasawaMusicBot.config import BOT_NAME as bn
from YuiHirasawaMusicBot.config import DURATION_LIMIT
from YuiHirasawaMusicBot.config import UPDATES_CHANNEL as updateschannel
from YuiHirasawaMusicBot.config import que
from YuiHirasawaMusicBot.function.admins import admins as a
from YuiHirasawaMusicBot.helpers.errors import DurationLimitError
from YuiHirasawaMusicBot.helpers.decorators import errors
from YuiHirasawaMusicBot.helpers.admins import get_administrators
from YuiHirasawaMusicBot.helpers.channelmusic import get_chat_id
from YuiHirasawaMusicBot.helpers.decorators import authorized_users_only
from YuiHirasawaMusicBot.helpers.filters import command
from YuiHirasawaMusicBot.helpers.filters import other_filters
from YuiHirasawaMusicBot.helpers.gets import get_file_name
from YuiHirasawaMusicBot.services.callsmusic import callsmusic
from YuiHirasawaMusicBot.services.callsmusic import client as USER
from YuiHirasawaMusicBot.services.converter.converter import convert
from YuiHirasawaMusicBot.services.downloaders import youtube
from YuiHirasawaMusicBot.services.queues import queues
from YuiHirasawaMusicBot.config import BOT_USERNAME as bot
from YuiHirasawaMusicBot.config import ASSISTANT_NAME

chat_id = None


@Client.on_message(filters.command(["channelplaylist","cplaylist","القناة قائمه الشتغيل","القناه قائمة الشتغيل","القناه قائمه الشتغيل","القناة قائمة التشغيل","channelplaylist@{bot}","cplaylist@{bot}","القناة قائمه الشتغيل@{bot}","القناه قائمة الشتغيل@{bot}","القناه قائمه الشتغيل@{bot}","القناة قائمة التشغيل@{bot}"]) & ~filters.private & ~filters.bot)
async def playlist(client, message):
    try:
      lel = await client.get_chat(message.chat.id)
      lol = lel.linked_chat.id
    except:
      message.reply("لم يتم ربط القناه ?")
      return
    global que
    queue = que.get(lol)
    if not queue:
        await message.reply_text("Player is idle")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "<b>يشتغل الان</b> in {}".format(lel.linked_chat.title)
    msg += "\n- " + now_playing
    msg += "\n- مطلوب من قبل " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "<b>الدور</b>"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n- {name}"
            msg += f"\n- مطلوب من قبل {usr}\n"
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
            stats += "مطلوب من قبل : {}".format(queue[0][1].mention)
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
                InlineKeyboardButton("⏹", "cleave"),
                InlineKeyboardButton("⏸", "cpuse"),
                InlineKeyboardButton("▶️", "cresume"),
                InlineKeyboardButton("⏭", "cskip"),
            ],
            [
                InlineKeyboardButton("قائمه التشغيل 📖", "cplaylist"),
            ],
            [InlineKeyboardButton("❌ اغلاق", "ccls")],
        ]
    )
    return mar


@Client.on_message(filters.command(["channelcurrent","ccurrent","القناة مسار","القناه مسار","channelcurrent@{bot}","ccurrent@{bot}","القناة مسار@{bot}","القناه مسار@{bot}"]) & ~filters.private & ~filters.bot)
async def ee(client, message):
    try:
      lel = await client.get_chat(message.chat.id)
      lol = lel.linked_chat.id
      conv = lel.linked_chat
    except:
      await message.reply("لم يتم ربط القناه ")
      return
    queue = que.get(lol)
    stats = updated_stats(conv, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("لا توجد محادثة صوتية قيد التشغيل في هذه الدردشة")


@Client.on_message(filters.command(["channelplayer","cplayer"]) & ~filters.private & ~filters.bot)
@authorized_users_only
async def settings(client, message):
    playing = None
    try:
      lel = await client.get_chat(message.chat.id)
      lol = lel.linked_chat.id
      conv = lel.linked_chat
    except:
      await message.reply("لم يتم ربط القناه ")
      return
    queue = que.get(lol)
    stats = updated_stats(conv, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause"))

        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("لا توجد محادثة صوتية قيد التشغيل في هذه الدردشة")


@Client.on_callback_query(filters.regex(pattern=r"^(cplaylist)$"))
async def p_cb(b, cb):
    global que
    try:
      lel = await client.get_chat(cb.message.chat.id)
      lol = lel.linked_chat.id
      conv = lel.linked_chat
    except:
      return    
    que.get(lol)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(lol)
        if not queue:
            await cb.message.edit("مشغل الموسيقي معطل")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**يشتغل الان** in {}".format(conv.title)
        msg += "\n- " + now_playing
        msg += "\n- مطلوب من قبل " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**الدور**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- مطلوب من قبل {usr}\n"
        await cb.message.edit(msg)


@Client.on_callback_query(
    filters.regex(pattern=r"^(cplay|cpause|cskip|cleave|cpuse|cresume|cmenu|ccls)$")
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
      try:
        lel = await b.get_chat(cb.message.chat.id)
        lol = lel.linked_chat.id
        conv = lel.linked_chat
        chet_id = lol
      except:
        return
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat
    

    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "cpause":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "paused"
        ):
            await cb.answer("الدردشة غير متصلة!", show_alert=True)
        else:
            callsmusic.pause(chet_id)
            await cb.answer("Music Paused!")
            await cb.message.edit(
                updated_stats(conv, qeue), reply_markup=r_ply("play")
            )

    elif type_ == "cplay":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "playing"
        ):
            await cb.answer("الدردشة غير متصلة!", show_alert=True)
        else:
            callsmusic.resume(chet_id)
            await cb.answer("Music Resumed!")
            await cb.message.edit(
                updated_stats(conv, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "cplaylist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("مشغل الموسيقي معطل")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**يشتغل الان** in {}".format(cb.message.chat.title)
        msg += "\n- " + now_playing
        msg += "\n- مطلوب من قبل " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**الدور**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- مطلوب من قبل {usr}\n"
        await cb.message.edit(msg)

    elif type_ == "cresume":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "playing"
        ):
            await cb.answer("الدردشة غير متصلة or already playng", show_alert=True)
        else:
            callsmusic.resume(chet_id)
            await cb.answer("Music Resumed!")
    elif type_ == "cpuse":
        if (chet_id not in callsmusic.active_chats) or (
            callsmusic.active_chats[chet_id] == "paused"
        ):
            await cb.answer("الدردشة غير متصلة or already paused", show_alert=True)
        else:
            callsmusic.pause(chet_id)
            await cb.answer("Music Paused!")
    elif type_ == "ccls":
        await cb.answer("Closed menu")
        await cb.message.delete()

    elif type_ == "cmenu":
        stats = updated_stats(conv, qeue)
        await cb.answer("Menu opened")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏹", "cleave"),
                    InlineKeyboardButton("⏸", "cpuse"),
                    InlineKeyboardButton("▶️", "cresume"),
                    InlineKeyboardButton("⏭", "cskip"),
                ],
                [
                    InlineKeyboardButton("قائمه التشغيل 📖", "cplaylist"),
                ],
                [InlineKeyboardButton("❌ اغلاق", "ccls")],
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)
    elif type_ == "cskip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.active_chats:
            await cb.answer("الدردشة غير متصلة!", show_alert=True)
        else:
            queues.task_done(chet_id)

            if queues.is_empty(chet_id):
                callsmusic.stop(chet_id)
                await cb.message.edit("- لا يوجد المزيد للتشغيل..\n- مغادرة المحادثة الصوتية!")
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

            callsmusic.stop(chet_id)
            await cb.message.edit("تم مغادره المحادثة!")
        else:
            await cb.answer("الدردشة غير متصلة!", show_alert=True)


@Client.on_message(filters.command(["channelplay","cplay","القناة تشغيل","القناه تشغيل","channelplay@{bot}","cplay@{bot}","القناة تشغيل@{bot}","القناه تشغيل@{bot}"]) & ~filters.private & ~filters.bot)
@authorized_users_only
async def play(_, message: Message):
    global que
    lel = await message.reply("🔄 <b>معالجة</b>")

    try:
      conchat = await _.get_chat(message.chat.id)
      conv = conchat.linked_chat
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("لم يتم ربط القناه ")
      return
    try:
      administrators = await get_administrators(conv)
    except:
      await message.reply("اضفني ادمن في القناة")
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
                        "<b>اضفني ادمن في القناة</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        "<b>انضم الحساب المساعد الي قناتك</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 خطأ هناك ضغط علي الحساب المساعد 🔴 \n تعذر الانضمام إلى قناتك بسبب الطلبات الكثيفة على الحساب المساعد تأكد من عدم حظر الحساب في المجموعة و القناة."
                        f"\n\nأو أضف يدويًا وحاول مرا اخري @{ASSISTANT_NAME}</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> الحساب المساعد ليس في هذه الدردشه اطلب من المسؤول كتابة `/انضم` حتا ينضم الحساب المساعد الي المجموعة</i>"
        )
        return
    message.from_user.id
    text_links = None
    message.from_user.first_name
    await lel.edit("🔎 <b>العثور على</b>")
    message.from_user.id
    user_id = message.from_user.id
    message.from_user.first_name
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    if message.reply_to_message:
        if message.reply_to_message.audio:
            pass
        entities = []
        toxt = message.reply_to_message.text \
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
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ طول الفيديو اكثر من {DURATION_LIMIT} لا يسمح لي بي التشغيل!"
            )
            return
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمه التشغيل", callback_data="cplaylist"),
                    InlineKeyboardButton("ااتحكم ⏯ ", callback_data="cmenu"),
                ],
                [InlineKeyboardButton(text="❌ اغلاق", callback_data="ccls")],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/f6086f8909fbfeb0844f2.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("🎵 **معالجة**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
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
                "Song not found.Try another song or maybe spell it properly."
            )
            print(str(e))
            return
        try:    
            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 60
            if (dur / 60) > DURATION_LIMIT:
                 await lel.edit(f"❌ طول الفيديو اكثر من  {DURATION_LIMIT} دقيقة لا يسمح لي بي التشغيل!")
                 return
        except:
            pass        
        dlurl = url
        dlurl=dlurl.replace("youtube","youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="cplaylist"),
                    InlineKeyboardButton("التحكم ⏯ ", callback_data="cmenu"),
                ],
                [InlineKeyboardButton(text="❌ اغلاق", callback_data="ccls")],
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
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
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
                 await lel.edit(f"❌ طول الفيديو اكثر من  {DURATION_LIMIT} دقيقة لا يسمح لي بي التشغيل!")
                 return
        except:
            pass
        dlurl = url
        dlurl=dlurl.replace("youtube","youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📖 قائمة التشغيل", callback_data="cplaylist"),
                    InlineKeyboardButton("التحكم ⏯ ", callback_data="cmenu"),
                ],
                [InlineKeyboardButton(text="❌ اغلاق", callback_data="ccls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))
    chat_id = chid
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
        chat_id = chid
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await callsmusic.set_stream(chat_id, file_path)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="▶️ <b>يشتغل</b> الاغنيه للتي طلبها {} في القناة المرتبطة".format(
                message.from_user.mention()
            ),
        )
        os.remove("final.png")
        return await lel.delete()


@Client.on_message(filters.command(["channeldplay","cdplay","القناة ديزر تشغيل","القناه ديزر تشغيل","channeldplay@{bot}","cdplay@{bot}","القناة ديزر تشغيل@{bot}","القناه ديزر تشغيل@{bot}"]) & ~filters.private & ~filters.bot)
@authorized_users_only
async def deezer(client: Client, message_: Message):
    global que
    lel = await message_.reply("🔄 <b>معالجة</b>")

    try:
      conchat = await client.get_chat(message_.chat.id)
      conid = conchat.linked_chat.id
      conv = conchat.linked_chat
      chid = conid
    except:
      await message_.reply("لم يتم ربط القناه ")
      return
    try:
      administrators = await get_administrators(conv)
    except:
      await message.reply("اضفني ادمن في القناة") 
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
                        "<b>تذكر أن تضيف المساعد إلى قناتك</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>اضفني ادمن في قناتك</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        "<b>انضم الحساب المساعد الي قناتك</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 خطأ هناك ضغط علي الحساب المساعد 🔴 \n تعذر الانضمام إلى قناتك بسبب الطلبات الكثيفة على الحساب المساعد تأكد من عدم حظر الحساب في المجموعة و القناة."
                        f"\n\nأو أضف يدويًا وحاول مرا اخري @{ASSISTANT_NAME}</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> الحساب المساعد ليس في هذه الدردشه اطلب من المسؤول كتابة `/انضم` حتا ينضم الحساب المساعد الي المجموعة</i>"
        )
        return
    requested_by = message_.from_user.first_name

    text = message_.text.split(" ", 1)
    queryy = text[1]
    query=queryy
    res = lel
    await res.edit(f"جاري البحث 🔍 عن `{queryy}` علي ديزر")
    try:
        songs = await arq.deezer(query,1)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        title = songs.result[0].title
        url = songs.result[0].url
        artist = songs.result[0].artist
        duration = songs.result[0].duration
        thumbnail = songs.result[0].thumbnail
    except:
        await res.edit("لم اجد نتائج!")
        return
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📖 قائمة التشغيل", callback_data="cplaylist"),
                InlineKeyboardButton("التحكم ⏯ ", callback_data="cmenu"),
            ],
            [InlineKeyboardButton(text="❌ Close", callback_data="ccls")],
        ]
    )
    file_path = await convert(wget.download(url))
    await res.edit("جاري توليد الصورة المصغرة")
    await generate_cover(requested_by, title, artist, duration, thumbnail)
    chat_id = chid
    if chat_id in callsmusic.active_chats:
        await res.edit("اضاف الي قائمة الانتظار")
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
    await callsmusic.set_stream(chat_id, file_path)
    await res.delete()

    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"يشتغل [{title}]({url}) عبر ديزر في القناة المرتبطة",
    )
    os.remove("final.png")


@Client.on_message(filters.command(["channelsplay","csplay","القناة سافن تشغيل","القناه سافن تشغيل","channelsplay@{bot}","csplay@{bot}","القناة سافن تشغيل@{bot}","القناه سافن تشغيل@{bot}"]) & ~filters.private & ~filters.bot)
@authorized_users_only
async def jiosaavn(client: Client, message_: Message):
    global que
    lel = await message_.reply("🔄 **معالجة**")
    try:
      conchat = await client.get_chat(message_.chat.id)
      conid = conchat.linked_chat.id
      conv = conchat.linked_chat
      chid = conid
    except:
      await message_.reply("لم يتم ربط القناه ")
      return
    try:
      administrators = await get_administrators(conv)
    except:
      await message.reply("اضفني ادمن في القناة")
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
                        "<b>تذكر أن تضيف المساعد إلى قناتك</b>",
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
                    await lel.edit(
                        "<b>انضم الحساب المساعد الي قناتك</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>🔴 خطأ هناك ضغط علي الحساب المساعد 🔴 \n تعذر الانضمام إلى قناتك بسبب الطلبات الكثيفة على الحساب المساعد تأكد من عدم حظر الحساب في المجموعة و القناة."
                        f"\n\nأو أضف يدويًا وحاول مرا اخري @{ASSISTANT_NAME}</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            "<i> الحساب المساعد ليس في هذه القناة ، اطلب من مسؤول القناة إرسال \n /انضم او /تشغيل \nالأمر لأول مرة أو إضافة الحساب المساعد يدويًا </i>"
        )
        return
    requested_by = message_.from_user.first_name
    chat_id = message_.chat.id
    text = message_.text.split(" ", 1)
    query = text[1]
    res = lel
    await res.edit(f"🔎 جاري البحث عن `{query}` علي موقع سافن")
    try:
        songs = await arq.saavn(query)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        sname = songs.result[0].song
        slink = songs.result[0].media_url
        ssingers = songs.result[0].singers
        sthumb = "https://telegra.ph/file/f6086f8909fbfeb0844f2.png"
        sduration = int(songs.result[0].duration)
    except Exception as e:
        await res.edit("لم اجد اي نتائج")
        print(str(e))
        return
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📖 قائمة التشغيل", callback_data="cplaylist"),
                InlineKeyboardButton("التحكم ⏯ ", callback_data="cmenu"),
            ],
            [InlineKeyboardButton(text="❌ اغلاق", callback_data="ccls")],
        ]
    )
    file_path = await convert(wget.download(slink))
    chat_id = chid
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
    await callsmusic.set_stream(chat_id, file_path)
    await res.edit("Generating Thumbnail.")
    await generate_cover(requested_by, sname, ssingers, sduration, sthumb)
    await res.delete()
    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"يشتغل {sname} في القناة المرتبطة",
    )
    os.remove("final.png")
