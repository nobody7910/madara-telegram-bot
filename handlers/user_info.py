import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type in ["group", "supergroup"] and message.reply_to_message:
        user = message.reply_to_message.from_user
    
    # Fetch all profile photos without a limit
    photos = await context.bot.get_user_profile_photos(user.id)
    if photos.photos:
        for photo in photos.photos:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=photo[-1].file_id,
                caption=f"One of {user.first_name}’s PFPs! 🔥"
            )
    else:
        await message.reply_text(f"Oops, {user.first_name} has no PFPs to show off! 😛")