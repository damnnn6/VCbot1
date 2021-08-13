from pyrogram import Client
import asyncio
from YuiHirasawaMusicBot.config import SUDO_USERS
from YuiHirasawaMusicBot.config import PMPERMIT
from YuiHirasawaMusicBot.config import BOT_USERNAME
from YuiHirasawaMusicBot.config import SUDO_USERNAME
from pyrogram import filters
from pyrogram.types import Message
from YuiHirasawaMusicBot.services.callsmusic import client as USER
from YuiHirasawaMusicBot.config import UPDATES_CHANNEL
from YuiHirasawaMusicBot.config import SUPPORT_GROUP

PMSET =True
pchats = []

@USER.on_message(filters.text(["join","انضم","userbotjoin"]) & filters.private & ~filters.bot)
async def pmPermit(client: USER, message: Message):
    link = message.text.split(" ", 1)[1]
            await USER.join_chat(link)
            await message.reply_text("حسنا لقد انضممت\nفي حاله لم انضم قم بي التاكد من الرابط او انني لست محظور")
            return

@USER.on_message(filters.text & filters.private & ~filters.me & ~filters.bot)
async def pmPermit(client: USER, message: Message):
    if PMPERMIT == "ENABLE":
        if PMSET:
            chat_id = message.chat.id
            if chat_id in pchats:
                return
            await USER.send_message(
                message.chat.id,
                f"- مرحبا انا الحساب المساعد لي البوت @{BOT_USERNAME}\n- يمكنك كتابه `/انضم `+ رابط المجموعه حتا انضم اليها\n- مطور البوت @{SUDO_USERNAME}\n- قناة البوت @{UPDATES_CHANNEL}\n- جروب الدعم @{SUPPORT_GROUP}",
            )
            return

    
@Client.on_message(filters.command(["pmpermit","رد الخاص",f"رد الخاص@{BOT_USERNAME}",f"pmpermit@{BOT_USERNAME}"]))
async def bye(client: Client, message: Message):
    if message.from_user.id in SUDO_USERS:
        global PMSET
        text = message.text.split(" ", 1)
        queryy = text[1]
        if queryy == "on" or queryy == "تفعيل":
            PMSET = True
            await message.reply_text("تم تفعيل رد الخاص")
            return
        if queryy == "off" or queryy == "تعطيل":
            PMSET = None
            await message.reply_text("تم تعطيل رد الخاص")
            return
    
