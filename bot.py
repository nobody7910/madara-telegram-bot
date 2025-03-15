# bot.py
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
from config import BOT_TOKEN
from handlers.general_commands import start, help_command, commands_menu
from handlers.group_stats import get_group_stats, get_top_members, get_message_frequency
from handlers.user_info import get_user_info
from handlers.group import (
    stat_command, info_command, mute_command, unmute_command, top_command,
    active_command, track_messages, leaderboard_command, handle_stat_callback,
    members_command, rank_command, warn_command, kick_command, afk_command,
    welcome_new_member, cancel_command, ban_command
)
from handlers.fun import register_fun_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def register_handlers(application):
    logger.info("Registering handlers...")
    # Basic commands (no admin needed)
    application.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("start", start, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("photo", get_user_info))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("active", active_command))
    application.add_handler(CommandHandler("rank", rank_command))
    application.add_handler(CommandHandler("group_stats", get_group_stats))
    application.add_handler(CommandHandler("top_members", get_top_members))
    application.add_handler(CommandHandler("message_freq", get_message_frequency))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("afk", afk_command))
    
    # Fun commands (no admin needed)
    register_fun_handlers(application)

    # Admin-only commands with check
    async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd_func):
        chat = update.effective_chat
        user = update.effective_user
        if chat.type in ["group", "supergroup"]:
            admins = await context.bot.get_chat_administrators(chat.id)
            if user.id not in [admin.user.id for admin in admins]:
                await update.message.reply_text(
                    "🤓 Yo, I need admin powers to do that! Make me an admin, fam!"
                )
                return
        await cmd_func(update, context)
    
    application.add_handler(CommandHandler("mute", lambda u, c: check_admin(u, c, mute_command)))
    application.add_handler(CommandHandler("unmute", lambda u, c: check_admin(u, c, unmute_command)))
    application.add_handler(CommandHandler("warn", lambda u, c: check_admin(u, c, warn_command)))
    application.add_handler(CommandHandler("kick", lambda u, c: check_admin(u, c, kick_command)))
    application.add_handler(CommandHandler("members", lambda u, c: check_admin(u, c, members_command)))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("ban", lambda u, c: check_admin(u, c, ban_command)))  # Added ban command

    # Message tracking, welcome, and callbacks
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))  # Added for welcome
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))
    application.add_handler(CallbackQueryHandler(handle_stat_callback, pattern=r'^stat_'))
    application.add_handler(CallbackQueryHandler(help_command, pattern=r'^(help_|fun_)'))
    application.add_handler(CallbackQueryHandler(commands_menu, pattern=r'^(commands_start_|cmd_)'))  # Updated to handle both patterns
    application.add_handler(CallbackQueryHandler(lambda update, context: update.callback_query.answer(), pattern=r'^noop$'))  # No-op for disabled buttons
    application.add_handler(CallbackQueryHandler(lambda update, context: update.callback_query.message.delete(), pattern=r'^commands_close$'))  # Close button
    application.add_handler(CallbackQueryHandler(lambda update, context: start(update, context), pattern=r'^commands_back$'))  # Back to start menu
    logger.info("Handlers registered successfully.")

def main() -> None:
    logger.info("Starting bot...")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set.")
        raise ValueError("BOT_TOKEN is required but not provided.")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("Application built successfully.")
        register_handlers(application)
        logger.info("Starting polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    logger.info("Bot script initiated.")
    main()