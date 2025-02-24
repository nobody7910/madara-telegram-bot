import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ChatMemberHandler, CallbackQueryHandler, CommandHandler, filters
from handlers.pm import start_pm, help_command, info
from handlers.group import (start_group, stats, stat, members, top, mute, photo, active, help_command as group_help)
from utils.helpers import get_user_photo, get_chat_photo

TOKEN = os.environ.get("TOKEN", "YOUR_BOT_TOKEN_HERE")

async def chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.my_chat_member and update.my_chat_member.new_chat_member.status == "member":
        chat = update.my_chat_member.chat
        user = update.my_chat_member.from_user
        welcome_text = (
            f"Hey @{user.username or user.first_name}, thanks for adding me to *{chat.title}*!\n"
            "I’m here to analyze and spice up your group. Let’s get started!"
        )
        keyboard = [[InlineKeyboardButton("See Commands", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat.id, text=welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        await group_help(update, context)

def main() -> None:
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
    application.add_handler(CommandHandler("help", group_help, filters=filters.ChatType.GROUPS))

    application.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()