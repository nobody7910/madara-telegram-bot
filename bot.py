# bot.py
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from config import BOT_TOKEN
from handlers.general_commands import start as general_start, help_command
from handlers.group_stats import get_group_stats, get_top_members, get_message_frequency
from handlers.user_info import get_user_info
from handlers.group import (
    stat_command, info_command, mute_command, unmute_command, top_command,
    active_command, track_messages, leaderboard_command, handle_stat_callback,
    members_command, rank_command
)
from handlers.pm import start_command as pm_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def register_handlers(application):
    logger.info("Registering handlers...")
    # PM Commands
    application.add_handler(CommandHandler("start", pm_start, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", help_command))
    # Group Commands
    application.add_handler(CommandHandler("start", general_start, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("photo", get_user_info))  # Reusing for PFP
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("members", members_command))
    application.add_handler(CommandHandler("rank", rank_command))
    application.add_handler(CommandHandler("group_stats", get_group_stats))
    application.add_handler(CommandHandler("top_members", get_top_members))
    application.add_handler(CommandHandler("message_freq", get_message_frequency))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("active", active_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))
    application.add_handler(CallbackQueryHandler(handle_stat_callback, pattern=r'^stat_'))
    application.add_handler(CallbackQueryHandler(help_command, pattern=r'^help_'))
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