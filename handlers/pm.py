from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.helpers import get_user_photo, bot_uptime

async def start_pm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    photo = await get_user_photo(context.bot, user.id)
    intro_text = (
        f"*Hey {user.first_name}!* 👋\n"
        f"[{user.username or user.full_name}]\n"
        "I’m @Madara7_chat_bot—your group stats guru! Add me to a group to unlock my powers.\n"
        "In PM, only /start, /help, and /info work."
    )
    keyboard = [[InlineKeyboardButton("Add me to a group", url=f"https://t.me/Madara7_chat_bot?startgroup=true")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if photo:
        await update.message.reply_photo(photo=photo, caption=intro_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(intro_text, parse_mode="Markdown", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    photo = await get_user_photo(context.bot, user.id)
    help_text = (
        f"*Hey {user.full_name}, here’s my command arsenal!*\n\n"
        "*PM Commands:*\n"
        "/start@Madara7_chat_bot - Get my intro and a group-add button\n"
        "/help@Madara7_chat_bot - See this detailed command rundown\n"
        "/info@Madara7_chat_bot - Check how long I’ve been awake\n\n"
        "*Group Commands:*\n"
        "/start@Madara7_chat_bot - A flashy welcome with my pic and buttons\n"
        "/stats@Madara7_chat_bot - Group overview (members, creation date)\n"
        "/stat@Madara7_chat_bot - User stats (username, ID, status, join date, etc.; reply or self)\n"
        "/members@Madara7_chat_bot - Total member count in the group\n"
        "/top@Madara7_chat_bot - Rank top 5 members (simulated messages)\n"
        "/mute@Madara7_chat_bot - Silence a user (reply required, needs admin rights)\n"
        "/photo@Madara7_chat_bot - Show profile pics (reply or self, up to 5)\n"
        "/active@Madara7_chat_bot - List top 3 active members (simulated)\n"
        "/rank@Madara7_chat_bot - Randomly rank a member with flair\n"
        "/help@Madara7_chat_bot - Redirects you here for the full scoop\n\n"
        "*Note:* Some features (e.g., message counts) are simulated due to Telegram limits."
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=help_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uptime_str = bot_uptime()
    await update.message.reply_text(f"*Bot Uptime:* {uptime_str}", parse_mode="Markdown")