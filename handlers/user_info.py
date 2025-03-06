# handlers/user_info.py
from telegram import Update
from telegram.ext import ContextTypes

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieve information about a user."""
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to get their info.")
        return
    
    user = update.message.reply_to_message.from_user
    
    user_info = (
        f"👤 User Information:\n"
        f"Name: {user.first_name} {user.last_name or ''}\n"
        f"Username: @{user.username or 'No username'}\n"
        f"User ID: {user.id}"
    )
    await update.message.reply_text(user_info)
    