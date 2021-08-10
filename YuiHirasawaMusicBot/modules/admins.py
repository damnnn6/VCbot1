from asyncio import QueueEmpty
from pyrogram import Client 
from pyrogram import filters
from pyrogram.types import Message

from YuiHirasawaMusicBot.config import que
from YuiHirasawaMusicBot.function.admins import set
from YuiHirasawaMusicBot.helpers.channelmusic import get_chat_id
from YuiHirasawaMusicBot.helpers.decorators import authorized_users_only
from YuiHirasawaMusicBot.helpers.decorators import errors
from YuiHirasawaMusicBot.helpers.filters import command
from YuiHirasawaMusicBot.helpers.filters import other_filters
from YuiHirasawaMusicBot.services.callsmusic import callsmusic
from YuiHirasawaMusicBot.services.queues import queues


@Client.on_message(filters.command("ضبط الادمنية"))
async def update_admin(client, message: Message):
    chat_id = get_chat_id(message.chat)
    set(
        chat_id,
        [
            member.user
            for member in await message.chat.get_members(filter="المسؤولين")
        ],
    )
    await message.reply_text("❇️ تم تحديث ذاكرة التخزين المؤقت للمسؤول")


@Client.on_message(command("توقف") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "pause"
    ):
        await message.reply_text("❗ لا شيئ مشغل الان !")
    else:
        callsmusic.pause(chat_id)
        await message.reply_text("▶️ متوقف !")


@Client.on_message(command("استئناف") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "playing"
    ):
        await message.reply_text("❗ لم يتم إيقاف أي شيء مؤقتًا‌‌!")
    else:
        callsmusic.resume(chat_id)
        await message.reply_text("⏸ مستأنـف!")


@Client.on_message(command("انهاء") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ لا شيئ مشغل الان !")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        await callsmusic.stop(chat_id)
        await message.reply_text("❌ توقف البوت عن العمل !")


@Client.on_message(command("تخطي") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ لا شيء مشغل للتخطي!")
    else:
        queues.task_done(chat_id)
        if queues.is_empty(chat_id):
            await callsmusic.stop(chat_id)
        else:
            await callsmusic.set_stream(
                chat_id, 
                queues.get(chat_id)["file"]
            )

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"- تم تخطي **{skip[0]}**\n- يشغل الان **{qeue[0][0]}**")


@Client.on_message(filters.command("المشرفين"))
@errors
async def admincache(client, message: Message):
    set(
        message.chat.id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("❇️ تم تحديث ذاكرة التخزين المؤقت للمسؤول !")
