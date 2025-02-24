from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from utils.helpers import get_user_photo, get_chat_photo
from datetime import datetime

async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    welcome_text = (
        f"*Welcome to {chat.title}!* 🎉\n"
        "I’m GroupAnalyzerBot—ready to analyze and assist!\n"
        "For full power, grant me admin rights (delete messages, ban users, pin messages, change info).\n"
        "Use /help to see my tricks!"
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=welcome_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    member_count = await context.bot.get_chat_member_count(chat.id)
    creation_date = datetime.fromtimestamp(chat.id / (1 << 32)).strftime('%Y-%m-%d')
    photo = await get_chat_photo(context.bot, chat.id)
    stats_text = (
        f"*Group: {chat.title}*\n"
        f"Members: {member_count}\n"
        f"Created: {creation_date} (approx)"
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=stats_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(stats_text, parse_mode="Markdown")

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        member = await context.bot.get_chat_member(chat.id, user.id)
        messages = "Unknown (API limit)"
        photo = await get_user_photo(context.bot, user.id)
        stat_text = (
            f"*User: {user.full_name}*\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Messages: {messages}"
        )
    else:
        user = update.message.from_user
        member = await context.bot.get_chat_member(chat.id, user.id)
        messages = "Unknown (API limit)"
        photo = await get_user_photo(context.bot, user.id)
        stat_text = (
            f"*Your Stats, {user.full_name}!*\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Messages: {messages}"
        )
    if photo:
        await update.message.reply_photo(photo=photo, caption=stat_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(stat_text, parse_mode="Markdown")

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"*Total members in {chat.title}:* {count}", parse_mode="Markdown")
    if photo:
        await update.message.reply_photo(photo=photo, caption=f"*Total members in {chat.title}:* {count}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"*Total members in {chat.title}:* {count}", parse_mode="Markdown")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption="*Top 5 users coming soon!* (Requires message tracking)", parse_mode="Markdown")
    else:
        await update.message.reply_text("*Top 5 users coming soon!* (Requires message tracking)", parse_mode="Markdown")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_restrict_members:
            await context.bot.restrict_chat_member(chat.id, user.id, permissions=ChatPermissions(can_send_messages=False))
            photo = await get_user_photo(context.bot, user.id)
            if photo:
                await update.message.reply_photo(photo=photo, caption=f"*Muted {user.full_name}!*", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"*Muted {user.full_name}!*", parse_mode="Markdown")
        else:
            await update.message.reply_text("*I need admin rights to mute users!*", parse_mode="Markdown")
    else:
        await update.message.reply_text("*Reply to a message with /mute to mute that user!*", parse_mode="Markdown")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption=f"*Group photo of {chat.title}* 📸", parse_mode="Markdown")
    else:
        await update.message.reply_text("*This group has no photo!*", parse_mode="Markdown")

async def active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption="*Last active user coming soon!* (Requires activity tracking)", parse_mode="Markdown")
    else:
        await update.message.reply_text("*Last active user coming soon!* (Requires activity tracking)", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    help_text = (
        "*Here’s what I can do in groups:*\n"
        "/start - Welcome message\n/stats - Group stats\n/stat - User stats (reply or self)\n"
        "/members - Member count\n/top - Top 5 users\n/mute - Toggle mute\n/photo - Group photo\n"
        "/active - Last active user\n/help - This list"
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=help_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")