# Credits Daisyxmusic
# Copyright (C) 2021  Inukaasith | Bruh_0x

from time import time
from datetime import datetime

import asyncio

from pyrogram import Client, filters
from pyrogram.types import Dialog, Chat, Message
from pyrogram.errors import UserAlreadyParticipant

from YuiHirasawaMusicBot.services.callsmusic.callsmusic import client as pakaya
from YuiHirasawaMusicBot.config import SUDO_USERS
from YuiHirasawaMusicBot.config import BOT_USERNAME

@Client.on_message(filters.command(["اذاعه المساعد",f"اذاعه المساعد@{BOT_USERNAME}"]))
async def broadcast(_, message: Message):
    sent=0
    failed=0
    if message.from_user.id not in SUDO_USERS:
        await message.reply("بس لعب!")
        return
    else:
        wtf = await message.reply("`جاري بدء الاذاعه...`")
        if not message.reply_to_message:
            await wtf.edit("من فضلك قم بي الرد علي الرساله 🥺!")
            return
        lmao = message.reply_to_message.text
        async for dialog in pakaya.iter_dialogs():
            try:
                await pakaya.send_message(dialog.chat.id, lmao)
                sent = sent+1
                await wtf.edit(f"`الاذاعة...` \n\n**ارسلت الي:** `{sent}` محادثة \n**فشل الارسال الي:** {failed} محادثة")
            except:
                failed=failed+1
                await wtf.edit(f"`الاذاعة...` \n\n**ارسلت الي:** `{sent}` محادثة \n**فشل الارسال الي:** {failed} محادثة")
            await asyncio.sleep(1)
        await message.reply_text(f"`انتهت الاذاعة 😌` \n\n**ارسلت الي:** `{sent}` محادثة \n**فشل الارسال الي:** {failed} محادثة")


@Client.on_message(filters.command(["ping",f"ping@{BOT_USERNAME}","السرعه",f"السرعه@{BOT_USERNAME}"]))
async def ping_pong(client: Client, message: Message):
    start = time()
    if message.from_user.id not in SUDO_USERS:
        await message.reply("بس لعب!")
        return
    else:
    m_reply = await message.reply("جاري قياس السرعه...")
    delta_ping = time() - start
    await m_reply.edit_text(
        f"السرعة `{delta_ping * 1000:.3f} MS`"
    )
    
    