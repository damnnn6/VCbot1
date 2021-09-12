from os import path

from pyrogram import filters
from pyrogram import Client
from pyrogram.types import Message, Voice
from YuiHirasawaMusicBot.services import callsmusic, converter, queues
from YuiHirasawaMusicBot.config import BOT_USERNAME, DURATION_LIMIT, BG_IMAGE
from YuiHirasawaMusicBot.services.downloaders import youtube
from YuiHirasawaMusicBot.helpers.filters import command
from YuiHirasawaMusicBot.helpers.decorators import errors
from YuiHirasawaMusicBot.helpers.errors import DurationLimitError
from YuiHirasawaMusicBot.helpers.gets import get_url, get_file_name
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from YuiHirasawaMusicBot.modules.play import generate_cover

@Client.on_message(filters.command(["موسيقي",f"موسيقي@{BOT_USERNAME}","audio","stream",f"audio@{BOT_USERNAME}",f"stream@{BOT_USERNAME}"]) & ~filters.private & ~filters.bot)
@errors
async def stream(_, message: Message):

    AY = await message.reply("🔄 معالجة")
    
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

    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ مقاطع الفيديو أطول من {DURATION_LIMIT} دقيقة غير مسموح لها بالتشغيل !"
            )

        file_name = get_file_name(audio)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name)) else file_name
        )
    elif url:
        file_path = await converter.convert(youtube.download(url))
    else:
        return await AY.edit_text(" لم اجد اغنية لتشغيلها!")

    if message.chat.id in callsmusic.callsmusic.active_chats:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
        photo=f"{BG_IMAGE}",
        reply_markup=keyboard,
        caption=f"#⌛ تم اضافه الموسيقي الي قائمة التشغيل {position}")
        return await AY.delete()
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        costumer = message.from_user.mention
        await message.reply_photo(
        photo=f"{BG_IMAGE}",
        reply_markup=keyboard,
        caption=f"🎧 **يشتغل الان** بوسطة {costumer}"
        )   
        return await AY.delete()
