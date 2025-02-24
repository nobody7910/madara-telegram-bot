import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from telegram import ChatPermissions
import time
from datetime import datetime

# Replace with your BotFather token
TOKEN = "7702619386:AAFHjs6Czsz9ocODx4RZ97CPKV47LuOysgo"
bot_start_time = time.time()  # Track bot uptime

# Command: /start (PM)
async def start_pm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    intro_text = (
        f"Hi {user.first_name}! I’m GroupAnalyzerBot.\n"
        "I analyze groups and provide stats. Add me to a group to get started!\n"
        "In PM, only /start works. Use /help for more info."
    )
    keyboard = [[InlineKeyboardButton("Add me to a group", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

# Command: /start (Group)
async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    await update.message.reply_text(
        f"Welcome to {chat.title}! I’m here to help with group stats and more.\n"
        "Grant me admin permissions (delete messages, ban users, pin messages, change info) for full functionality.\n"
        "Use /help to see all commands!"
    )

# Command: /help (PM and Group)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Here’s what I can do:\n"
        "PM:\n/start - Bot intro\n/help - Command list\n/info - Bot uptime\n"
        "Group:\n/start - Welcome message\n/stats - Group stats\n/stat - User stats (reply to a message)\n"
        "/members - Member count\n/top - Top 5 users\n/mute - Toggle mute\n/photo - Group photo\n"
        "/active - Last active user\n/help - This list"
    )
    await update.message.reply_text(help_text)

# Command: /info (PM only)
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uptime = time.time() - bot_start_time
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    await update.message.reply_text(f"Bot Uptime: {int(hours)}h {int(minutes)}m {int(seconds)}s")

# Command: /stats (Group)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    member_count = await context.bot.get_chat_member_count(chat.id)
    creation_date = datetime.fromtimestamp(chat.id / (1 << 32)).strftime('%Y-%m-%d')
    stats_text = (
        f"Group: {chat.title}\n"
        f"Members: {member_count}\n"
        f"Created: {creation_date} (approx)\n"
    )
    if chat.photo:
        await context.bot.send_photo(chat_id=chat.id, photo=chat.photo.big_file_id, caption=stats_text)
    else:
        await update.message.reply_text(stats_text)

# Command: /stat (Group, reply to a message)
async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        chat = update.message.chat
        member = await context.bot.get_chat_member(chat.id, user.id)
        messages = "Unknown (API limit)"  # Telegram API doesn’t provide message count
        stat_text = (
            f"User: {user.full_name}\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Messages: {messages}"
        )
        if user.photo:
            await context.bot.send_photo(chat_id=chat.id, photo=user.photo.big_file_id, caption=stat_text)
        else:
            await update.message.reply_text(stat_text)
    else:
        await update.message.reply_text("Reply to a message with /stat to see user stats!")

# Command: /members (Group)
async def members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"Total members in {chat.title}: {count}")

# Command: /top (Group, placeholder)
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Top 5 users feature coming soon! (Requires message tracking)")

# Command: /mute (Group)
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_restrict_members:
            await context.bot.restrict_chat_member(chat.id, user.id, permissions=ChatPermissions(can_send_messages=False))
            await update.message.reply_text(f"Muted {user.full_name}!")
        else:
            await update.message.reply_text("I need admin rights to mute users!")
    else:
        await update.message.reply_text("Reply to a message with /mute to mute that user!")

# Command: /photo (Group)
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if chat.photo:
        await context.bot.send_photo(chat_id=chat.id, photo=chat.photo.big_file_id, caption=f"Group photo of {chat.title}")
    else:
        await update.message.reply_text("This group has no photo!")

# Command: /active (Group, placeholder)
async def active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Last active user feature coming soon! (Requires activity tracking)")

# Main function to set up the bot
def main() -> None:
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # PM commands
    application.add_handler(CommandHandler("start", start_pm, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info, filters=filters.ChatType.PRIVATE))

    # Group commands
    application.add_handler(CommandHandler("start", start_group, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("stats", stats, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("stat", stat, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("members", members, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("top", top, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("mute", mute, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("photo", photo, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("active", active, filters=filters.ChatType.GROUPS))

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()