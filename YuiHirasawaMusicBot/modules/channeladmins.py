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
from YuiHirasawaMusicBot.config import BOT_USERNAME

@Client.on_message(filters.command(["channelpause","cpause","القناه توقف","القناة توقف",f"channelpause@{BOT_USERNAME}",f"cpause@{BOT_USERNAME}",f"القناه توقف@{BOT_USERNAME}",f"القناة توقف@{BOT_USERNAME}"]) & filters.group)
@errors
@authorized_users_only
async def pause(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("لم يتم ربط القناه")
      return    
    chat_id = chid
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "paused"
    ):
        await message.reply_text("❗ لا شيئ مشغل الان !")
    else:
        callsmusic.pause(chat_id)
        await message.reply_text("▶️ متوقف !")


@Client.on_message(filters.command(["channelresume","cresume","القناه استئناف","القناة استئناف",f"channelresume@{BOT_USERNAME}",f"cresume@{BOT_USERNAME}",f"القناه استئناف@{BOT_USERNAME}",f"القناة استئناف@{BOT_USERNAME}"]) & filters.group)
@errors
@authorized_users_only
async def resume(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("لم يتم ربط القناه")
      return    
    chat_id = chid
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "playing"
    ):
        await message.reply_text("❗ لم يتم إيقاف أي شيء مؤقتا !")
    else:
        callsmusic.resume(chat_id)
        await message.reply_text("⏸ اسـتـنـاف !")


@Client.on_message(filters.command(["channelend","cend","القناه انهاء","القناة انهاء",f"channelend@{BOT_USERNAME}",f"cend@{BOT_USERNAME}",f"القناه انهاء@{BOT_USERNAME}",f"القناة انهاء@{BOT_USERNAME}"]) & filters.group)
@errors
@authorized_users_only
async def stop(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("لم يتم ربط القناه")
      return    
    chat_id = chid
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ لا شيئ مشغل الان!")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        await callsmusic.stop(chat_id)
        await message.reply_text("❌ توقف البوت عن العمل!")


@Client.on_message(filters.command(["channelskip","cskip","القناه تخطي","القناة تخطي",f"channelskip@{BOT_USERNAME}",f"cskip@{BOT_USERNAME}",f"القناه تخطي@{BOT_USERNAME}",f"القناة تخطي@{BOT_USERNAME}"]) & filters.group)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("لم يتم ربط القناه")
      return    
    chat_id = chid
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ لا شيء مشغل للتخطي !")
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
    await message.reply_text(f"- تم تخطي **{skip[0]}**\n- يشتغل الان **{qeue[0][0]}**")


@Client.on_message(filters.command(["channelupdata","cupdata","القناه تحديث","القناة تحديث",f"channelupdata@{BOT_USERNAME}",f"cupdata@{BOT_USERNAME}",f"القناه تحديث@{BOT_USERNAME}",f"القناة تحديث@{BOT_USERNAME}"]) & filters.group)
@errors
async def admincache(client, message: Message):
    try:
      conchat = await client.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("لم يتم ربط القناه")
      return
    set(
        chid,
        [
            member.user
            for member in await conchat.linked_chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("❇️ تم تحديث قائمه المشرفين المؤقتا للقناه !")
