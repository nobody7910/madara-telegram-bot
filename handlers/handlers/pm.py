from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.helpers import get_user_photo, bot_uptime

async def start_pm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    photo = await get_user_photo(context.bot, user.id)
    intro_text = (
        f"*Hey {user.first_name}!* 👋\n"
        f"[{user.username or user.full_name}]\n"
        "I’m GroupAnalyzerBot—your group stats guru! Add me to a group to unlock my powers.\n"
        "In PM, only /start, /help, and /info work."
    )
    keyboard = [[InlineKeyboardButton("Add me to a group", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if photo:
        await update.message.reply_photo(photo=photo, caption=intro_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(intro_text, parse_mode="Markdown", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "*Here’s what I can do:*\n"
        "__PM:__\n/start - Bot intro\n/help - Command list\n/info - Bot uptime\n"
        "__Group:__\n/start - Welcome message\n/stats - Group stats\n/stat - User stats (reply or self)\n"
        "/members - Member count\n/top - Top 5 users\n/mute - Toggle mute\n/photo - Group photo\n"
        "/active - Last active user\n/help - Command list"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uptime_str = bot_uptime()
    await update.message.reply_text(f"*Bot Uptime:* {uptime_str}", parse_mode="Markdown")