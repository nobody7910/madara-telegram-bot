import asyncio
import os
import socket
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ChatMemberHandler, CallbackQueryHandler, CommandHandler, filters, ApplicationHandlerStop
import telegram  # For error handling
from handlers.pm import start_pm, help_command as pm_help_command, info as pm_info
from utils.helpers import get_user_photo, get_chat_photo
from handlers.group import (start_group, stats, stat, members, top, mute, unmute, photo, active, rank, info as group_info, help as group_help_command)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a new, valid token from BotFather
TOKEN = "7702619386:AAEXCt9dt3SfcW5xZN4FKN77jr0HURovZS0"  # Replace with your new token

async def chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.my_chat_member and update.my_chat_member.new_chat_member.status == "member":
        chat = update.my_chat_member.chat
        user = update.my_chat_member.from_user
        welcome_text = (
            f"Hey @{user.username or user.first_name}, thanks for adding me to *{chat.title}*!\n"
            "I’m @Madara7_chat_bot, here to analyze and spice things up. Let’s get started!"
        )
        keyboard = [[InlineKeyboardButton("See Commands", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat.id, text=welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        user = update.effective_user
        help_text = (
            f"*Hey {user.full_name}, here’s my command rundown!*\n\n"
            "*PM Commands:*\n"
            "/start@Madara7_chat_bot - Get my intro and a group-add button\n"
            "/help@Madara7_chat_bot - See this command list\n"
            "/info@Madara7_chat_bot - Check my uptime\n\n"
            "*Group Commands:*\n"
            "/start@Madara7_chat_bot - A flashy welcome with buttons\n"
            "/stats@Madara7_chat_bot - Group overview (members, creation date)\n"
            "/stat@Madara7_chat_bot - User stats (bio, username, etc.; reply or self)\n"
            "/members@Madara7_chat_bot - Total member count\n"
            "/top@Madara7_chat_bot - Rank top 5 admins (simulated activity)\n"
            "/mute@Madara7_chat_bot - Mute a user (admin-only, reply required)\n"
            "/unmute@Madara7_chat_bot - Unmute a user (admin-only, reply required)\n"
            "/photo@Madara7_chat_bot - Show profile pics (reply or self, up to 5)\n"
            "/active@Madara7_chat_bot - Show group activity status\n"
            "/rank@Madara7_chat_bot - Randomly rank a member\n"
            "/info@Madara7_chat_bot - Detailed user info in group\n"
            "/help@Madara7_chat_bot - Redirects you here\n\n"
            "*Note:* Some features are simulated due to Telegram limits."
        )
        await context.bot.send_message(chat_id=user.id, text=help_text, parse_mode="Markdown")
        await query.edit_message_text(
            text="*Redirected! Check your PM for the full command rundown!*",
            parse_mode="Markdown"
        )

async def dummy_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8000))
    server.listen(1)
    print("Dummy server started on port 8000")
    while True:
        await asyncio.sleep(3600)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors like conflicts and log them."""
    logger.error("Exception occurred:", exc_info=context.error)
    if isinstance(context.error, telegram.error.Conflict):
        logger.warning("Conflict detected: Another instance is running. Stopping this instance.")
        raise ApplicationHandlerStop

def main():
    application = Application.builder().token(TOKEN).build()

    # PM commands
    application.add_handler(CommandHandler("start", start_pm, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", pm_help_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("info", pm_info, filters=filters.ChatType.PRIVATE))

    # Group commands
    application.add_handler(CommandHandler("start", start_group, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("stats", stats, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("stat", stat, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("members", members, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("top", top, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("mute", mute, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("unmute", unmute, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("photo", photo, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("active", active, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("rank", rank, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("info", group_info, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("help", group_help_command, filters=filters.ChatType.GROUPS))

    # Additional handlers
    application.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Error handler
    application.add_error_handler(error_handler)

    loop = asyncio.get_event_loop()
    loop.create_task(dummy_server())

    print("Bot starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()