import asyncio
import os
import socket
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ChatMemberHandler, CallbackQueryHandler, CommandHandler, filters
from handlers.pm import start_pm, help_command as pm_help_command, info
from handlers.group import (start_group, stats, stat, members, top, mute, photo, active, rank, help_command as group_help_command)
from utils.helpers import get_user_photo, get_chat_photo

TOKEN = os.environ.get("TOKEN", "YOUR_BOT_TOKEN_HERE")

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
        await group_help_command(update, context)

async def dummy_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8000))  # Listen on port 8000 for Koyeb health check
    server.listen(1)
    print("Dummy server started on port 8000")
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour, keeping the server alive

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # PM commands
    application.add_handler(CommandHandler("start", start_pm, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", pm_help_command, filters=filters.ChatType.PRIVATE))
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
    application.add_handler(CommandHandler("rank", rank, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("help", group_help_command, filters=filters.ChatType.GROUPS))

    application.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the dummy server as a background task
    loop = asyncio.get_event_loop()
    loop.create_task(dummy_server())

    # Run polling in the main loop
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()