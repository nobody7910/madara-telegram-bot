# handlers/general_commands.py
from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    bot_intro = (
        "👋 Welcome to Group Analytics Bot! 📊\n\n"
        "I'm a powerful group management and analytics bot. Here's what I can do:\n"
        "• Provide detailed group statistics\n"
        "• Show top active members\n"
        "• Analyze message frequencies\n"
        "• Fetch user information\n"
        "• And much more!\n\n"
        "Use /help to see all available commands."
    )
    await update.message.reply_text(bot_intro)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message with all available commands."""
    help_text = (
        "🤖 Available Commands:\n"
        "/start - Bot introduction\n"
        "/help - Show this help message\n"
        "/group_stats - Get overall group statistics\n"
        "/top_members - Show most active members\n"
        "/message_freq - Analyze message frequency\n"
        "/user_info - Get information about a user\n"
    )
    await update.message.reply_text(help_text)