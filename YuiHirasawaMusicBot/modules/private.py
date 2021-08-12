import logging
from YuiHirasawaMusicBot.modules.msg import Messages as tr
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import Message
from YuiHirasawaMusicBot.config import ASSISTANT_NAME
from YuiHirasawaMusicBot.config import PROJECT_NAME
from YuiHirasawaMusicBot.config import SUPPORT_GROUP
from YuiHirasawaMusicBot.config import UPDATES_CHANNEL
from YuiHirasawaMusicBot.config import BOT_USERNAME
from YuiHirasawaMusicBot.config import SUDO_USERNAME
from YuiHirasawaMusicBot.config import COMMANDS
logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.private & filters.incoming & filters.commands(['/start']))
def _start(client, message):
    client.send_message(message.chat.id,
        text=tr.START_MSG.format(message.from_user.first_name + " " + message.from_user.last_name, message.from_user.id),
        parse_mode="markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ انقر لاضافتي لمجموعتك 🙋‍♀️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
                [
                    InlineKeyboardButton(
                        "🔊 قناة البوت", url=f"https://t.me/{UPDATES_CHANNEL}"), 
                    InlineKeyboardButton(
                        "🛠 المطور", url=f"https://t.me/{SUDO_USERNAME}")
                ],[
                    InlineKeyboardButton(
                         "🔐 الاوامر", url=f"https://telegra.ph/0150---أحمد-عياد----𝘼𝙃𝙈𝙀𝘿-Lonely-08-10")
                ],[
                    InlineKeyboardButton(
                         "💬 جروب الدعم", url=f"https://t.me/{SUPPORT_GROUP}")
                ],[
                    InlineKeyboardButton(
                        PROJECT_NAME, url=f"https://t.me/{ASSISTANT_NAME}")],
            ]
        ),
        reply_to_message_id=message.message_id
        )
     
@Client.on_message(filters.private & filters.incoming & filters.command(['/help','مساعده','مساعدة','الاوامر']))
def _help(client, message):
    client.send_message(chat_id = message.chat.id,
        text = tr.HELP_MSG[1],
        parse_mode="markdown",
        disable_web_page_preview=True,
        disable_notification=True,
        reply_markup = InlineKeyboardMarkup(map(1)),
        reply_to_message_id = message.message_id
    )

help_callback_filter = filters.create(lambda _, __, query: query.data.startswith('help+'))

@Client.on_callback_query(help_callback_filter)
def help_answer(client, callback_query):
    chat_id = callback_query.from_user.id
    disable_web_page_preview=True
    message_id = callback_query.message.message_id
    msg = int(callback_query.data.split('+')[1])
    client.edit_message_text(chat_id=chat_id,    message_id=message_id,
        text=tr.HELP_MSG[msg],    reply_markup=InlineKeyboardMarkup(map(msg))
    )


def map(pos):
    if(pos==1):
        button = [
            [InlineKeyboardButton(text = '▶️', callback_data = "help+2")]
        ]
    elif(pos==len(tr.HELP_MSG)-1):
        button = [
            [InlineKeyboardButton("➕ انقر لاضافتي لمجموعتك 🙋‍♀️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton(text = '🔊 قناة البوت', url=f"https://t.me/{UPDATES_CHANNEL}"),
             InlineKeyboardButton(text = '💬 جروب الدعم', url=f"https://t.me/{SUPPORT_GROUP}")],
            [InlineKeyboardButton(text = '◀️', callback_data = f"help+{pos-1}")]
        ]
    else:
        button = [
            [
                InlineKeyboardButton(text = '◀️', callback_data = f"help+{pos-1}"),
                InlineKeyboardButton(text = '▶️', callback_data = f"help+{pos+1}")
            ],
        ]
    return button


@Client.on_message(filters.command(["اليوتيوب","بحث اليوتيوب",f"اليوتيوب@{BOT_USERNAME}",f"بحث اليوتيوب@{BOT_USERNAME}","/youtube",f"/youtube@{BOT_USERNAME}"]))
async def start(client: Client, message: Message):
    await message.reply_text(
        "💁🏻‍♂️ هل تريد البحث علي يوتيوب?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 قناة البوت", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                    InlineKeyboardButton(
                        "💬 جروب الدعم", url=f"https://t.me/{SUPPORT_GROUP}"
                    )
                ],    
                [    
                    InlineKeyboardButton(
                        "✅ نعم", switch_inline_query_current_chat=""
                    ),
                    InlineKeyboardButton(
                        "لا ❌", callback_data="close"
                    )
                ]
            ]
        )
    )
    
    
    