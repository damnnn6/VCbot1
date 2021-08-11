from pyrogram import Client
import asyncio
from YuiHirasawaMusicBot.config import SUDO_USERS
from YuiHirasawaMusicBot.config import PMPERMIT
from YuiHirasawaMusicBot.config import BOT_USERNAME
from YuiHirasawaMusicBot.config import SUDO_USERNAME
from pyrogram import filters
from pyrogram.types import Message
from YuiHirasawaMusicBot.services.callsmusic import client as USER

PMSET =True
pchats = []

@USER.on_message(filters.text & filters.private & ~filters.me & ~filters.bot)
async def pmPermit(client: USER, message: Message):
    if PMPERMIT == "ENABLE":
        if PMSET:
            chat_id = message.chat.id
            if chat_id in pchats:
                return
            await USER.send_message(
                message.chat.id,
                f"مرحبا انا الحساب المساعد لي البوت @{BOT_USERNAME}\nمطور البوت @{SUDO_USERNAME}",
            )
            return

@Client.on_message(filters.command(["تيست","test",f"تيست@{BOT_USERNAME}",f"test@{BOT_USERNAME}"]))
async def bye(client: Client, message: Message):
    if message.from_user.id in SUDO_USERS:
        global PMSET
        text = message.text.split(" ", 1)
        await message.reply_text(
                message.chat.id,
                f"بوت تشغيل الموسيقي يعمل بنجاح\nالبوت @{BOT_USERNAME}\nمطور البوت @{SUDO_USERNAME}\nالحساب المساعد @{ASSISTANT_NAME}",
            )
                return

@Client.on_message(filters.command(["تيست","test",f"تيست@{BOT_USERNAME}",f"test@{BOT_USERNAME}"]))
async def pmPermit(client: Client, message: Message):
    if message.from_user.id in SUDO_USERS:
        if PMSET:
            chat_id = message.chat.id
            if chat_id in pchats:
                return
            await message.reply_text(
                message.chat.id,
                f"بوت تشغيل الموسيقي يعمل بنجاح\nالبوت @{BOT_USERNAME}\nمطور البوت @{SUDO_USERNAME}\nالحساب المساعد @{ASSISTANT_NAME}",
            )
            return
            
@USER.on_message(filters.command(["تيست","test",f"تيست@{BOT_USERNAME}",f"test@{BOT_USERNAME}"]) & filters.private & filters.me)
async def pmPermit(client: USER, message: Message):
    if message.from_user.id in SUDO_USERS:
        if PMSET:
            chat_id = message.chat.id
            if chat_id in pchats:
                return
            await USER.send_message(
                message.chat.id,
                f"بوت تشغيل الموسيقي يعمل بنجاح\nالبوت @{BOT_USERNAME}\nمطور البوت @{SUDO_USERNAME}\nالحساب المساعد @{ASSISTANT_NAME}",
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
    
