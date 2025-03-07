# handlers/user_info.py
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    # Check for reply in groups
    if chat.type in ["group", "supergroup"] and message.reply_to_message:
        user = message.reply_to_message.from_user
    
    photos = await context.bot.get_user_profile_photos(user.id, limit=3)  # Get up to 3 recent PFPs
    if photos.photos:
        for photo in photos.photos:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=photo[-1].file_id,  # Largest size
                caption=f"One of {user.first_name}’s recent PFPs! 🔥"
            )
    else:
        await message.reply_text(f"Oops, {user.first_name} has no PFPs to show off! 😛")