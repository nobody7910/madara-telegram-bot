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
from handlers.general_commands import start as general_start, help_command as general_help
from handlers.group_stats import get_group_stats, get_top_members, get_message_frequency
from handlers.user_info import get_user_info
from handlers.group import (
    stat_command, info_command, mute_command, top_command, active_command,
    track_messages, leaderboard_command, handle_stat_callback
)
from handlers.pm import start_command as pm_start, help_command as pm_help
from aiohttp import web
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dummy HTTP health check endpoint
async def health_check(request):
    return web.Response(text="OK", status=200)

async def start_http_server():
    app = web.Application()
    app.add_routes([web.get('/health', health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("Health check server running on port 8080")

def register_handlers(application):
    logger.info("Registering handlers...")
    application.add_handler(CommandHandler("start", pm_start))
    application.add_handler(CommandHandler("help", pm_help))
    application.add_handler(CommandHandler("group_stats", get_group_stats))
    application.add_handler(CommandHandler("top_members", get_top_members))
    application.add_handler(CommandHandler("message_freq", get_message_frequency))
    application.add_handler(CommandHandler("user_info", get_user_info))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("active", active_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))
    application.add_handler(CallbackQueryHandler(handle_stat_callback, pattern=r'^stat_'))
    logger.info("Handlers registered successfully.")

async def main() -> None:
    logger.info("Starting bot...")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Please check environment variables.")
        raise ValueError("BOT_TOKEN is required but not provided.")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("Application built successfully.")
        register_handlers(application)
        
        # Start both the bot polling and HTTP server
        await asyncio.gather(
            start_http_server(),
            application.run_polling(allowed_updates=Update.ALL_TYPES)
        )
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    logger.info("Bot script initiated.")
    asyncio.run(main())