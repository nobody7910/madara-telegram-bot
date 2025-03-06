# handlers/pm.py
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome = (
        f"Yo {user.first_name}! What’s up? 😎\n"
        "I’m your chill bot—hit /help to see my moves!"
    )
    await update.message.reply_text(welcome)