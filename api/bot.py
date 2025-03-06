# api/bot.py
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    Dispatcher
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
from telegram.ext import ContextTypes
from aiohttp import web
import os
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the Application (runs once)
application = Application.builder().token(BOT_TOKEN).build()
dispatcher = application.dispatcher

def register_handlers(dispatcher):
    logger.info("Registering handlers...")
    dispatcher.add_handler(CommandHandler("start", pm_start))
    dispatcher.add_handler(CommandHandler("help", pm_help))
    dispatcher.add_handler(CommandHandler("group_stats", get_group_stats))
    dispatcher.add_handler(CommandHandler("top_members", get_top_members))
    dispatcher.add_handler(CommandHandler("message_freq", get_message_frequency))
    dispatcher.add_handler(CommandHandler("user_info", get_user_info))
    dispatcher.add_handler(CommandHandler("stat", stat_command))
    dispatcher.add_handler(CommandHandler("info", info_command))
    dispatcher.add_handler(CommandHandler("mute", mute_command))
    dispatcher.add_handler(CommandHandler("top", top_command))
    dispatcher.add_handler(CommandHandler("active", active_command))
    dispatcher.add_handler(CommandHandler("leaderboard", leaderboard_command))
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))
    dispatcher.add_handler(CallbackQueryHandler(handle_stat_callback, pattern=r'^stat_'))
    logger.info("Handlers registered successfully.")

# Register handlers once
register_handlers(dispatcher)

# Webhook handler
async def handle_webhook(request):
    try:
        if request.method == "POST":
            update_data = await request.json()
            update = Update.de_json(update_data, application.bot)
            await dispatcher.process_update(update)
            return web.Response(text="OK", status=200)
        return web.Response(text="Method not allowed", status=405)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return web.Response(text="Error", status=500)

# Vercel serverless function entry point
app = web.Application()
app.router.add_post('/', handle_webhook)

# Set webhook on startup (runs once when deployed)
async def set_webhook():
    webhook_url = f"https://{os.getenv('VERCEL_URL')}/api/bot"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

if __name__ == "__main__":
    # For local testing, not used in Vercel
    import asyncio
    asyncio.run(set_webhook())
    web.run_app(app, host="0.0.0.0", port=3000)