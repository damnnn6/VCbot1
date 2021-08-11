# Credits Daisyxmusic
# Copyright (C) 2021  Inukaasith | Bruh_0x


import asyncio

from pyrogram import Client, filters
from pyrogram.types import Dialog, Chat, Message
from pyrogram.errors import UserAlreadyParticipant

from YuiHirasawaMusicBot.services.callsmusic.callsmusic import client as pakaya
from YuiHirasawaMusicBot.config import SUDO_USERS

@Client.on_message(filters.command(["اذاعه"]))
async def broadcast(_, message: Message):
    sent=0
    failed=0
    if message.from_user.id not in SUDO_USERS:
        await message.reply("هل انت عبيط 😂!")
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
            await asyncio.sleep(3)
        await message.reply_text(f"`انتهت الاذاعة 😌` \n\n**ارسلت الي:** `{sent}` محادثة \n**فشل الارسال الي:** {failed} محادثة")
