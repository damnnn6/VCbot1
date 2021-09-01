from os import getenv
import os
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

que = {}
admins = {}
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
SESSION_NAME = getenv("SESSION_NAME")
BOT_TOKEN = getenv("BOT_TOKEN")
BOT_NAME = getenv("BOT_NAME", '√𝙼𝚄𝚂𝙸𝙲.."𖥕𝚅𝙴𝙽𝙼𝙾🎶')
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "SOURCEVENOM")
BG_IMAGE = getenv("BG_IMAGE", "https://telegra.ph/file/66d20cfdb5f398df9697a.jpg")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "AYVCMusicuser")
BOT_USERNAME = getenv("BOT_USERNAME", "AYVCMusicbot")
SUDO_USERNAME = getenv("SUDO_USERNAME", "ahmedyad200")
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "VC_SUP")
PROJECT_NAME = getenv("PROJECT_NAME", '√꧑ᥙ᥉Ꭵᥴ.."𖥕᥎ᥱꪀ꧑᥆🎵')
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "10"))
ARQ_API_KEY = getenv("ARQ_API_KEY", "LARVEY-XVIAOU-RZICIW-LUDGTE-ARQ")
PMPERMIT = getenv("PMPERMIT", "ENABLE")
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "944353237").split()))
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "").split())

