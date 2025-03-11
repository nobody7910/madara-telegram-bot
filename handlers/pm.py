# handlers/pm.py
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    
    photos = await context.bot.get_user_profile_photos(user.id, limit=1)
    intro = (
        f"🎉 Yo yo, {user.first_name}! Welcome to the party! 🎉\n"
        f"I’m your slick bot—hit /help for the rundown!\n"
    )
    
    keyboard = [[InlineKeyboardButton("Add me to a group", callback_data="add_to_group")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if photos.photos:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=photos.photos[0][-1].file_id,
            caption=intro,
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat.id,
            text=intro,
            reply_markup=reply_markup
        )