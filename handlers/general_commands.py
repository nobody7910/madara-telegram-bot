# handlers/general_commands.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    
    # Fetch user profile photos
    photos = await context.bot.get_user_profile_photos(user.id, limit=1)
    intro = (
        f"🎉 Yo yo, {user.first_name}! Welcome to the party! 🎉\n"
        "I’m your friendly neighborhood bot, here to spice up this group! "
        "Check out my tricks with /help!"
    )
    
    if photos.photos:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=photos.photos[0][-1].file_id,  # Largest size
            caption=intro
        )
    else:
        await context.bot.send_message(chat_id=chat.id, text=intro)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    is_group = chat.type in ["group", "supergroup"]
    
    # Command list with buttons
    keyboard = [
        [InlineKeyboardButton("📊 Stat", callback_data="help_stat"),
         InlineKeyboardButton("ℹ️ Info", callback_data="help_info")],
        [InlineKeyboardButton("📸 Photo", callback_data="help_photo"),
         InlineKeyboardButton("🔇 Mute", callback_data="help_mute")],
        [InlineKeyboardButton("🔊 Unmute", callback_data="help_unmute"),
         InlineKeyboardButton("👥 Members", callback_data="help_members")],
        [InlineKeyboardButton("🏆 Rank", callback_data="help_rank")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Bot PFP
    bot_photos = await context.bot.get_user_profile_photos(context.bot.id, limit=1)
    help_text = (
        "Hey there! I’m your cool bot! 😎\n"
        "Click a button to see what I can do!"
    )
    
    if bot_photos.photos:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=bot_photos.photos[0][-1].file_id,
            caption=help_text,
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat.id,
            text=help_text,
            reply_markup=reply_markup
        )

    # Handle button clicks
    query = update.callback_query
    if query:
        data = query.data
        if data == "help_stat":
            await query.edit_message_text("📊 /stat - Shows group message stats (today, yesterday, monthly).")
        elif data == "help_info":
            await query.edit_message_text("ℹ️ /info - Get dope info about a user!")
        elif data == "help_photo":
            await query.edit_message_text("📸 /photo - Snag your PFP or a replied user’s in groups!")
        elif data == "help_mute":
            await query.edit_message_text("🔇 /mute - Silence someone (admins only, with sass for admin targets)!")
        elif data == "help_unmute":
            await query.edit_message_text("🔊 /unmute - Free someone from the mute dungeon!")
        elif data == "help_members":
            await query.edit_message_text("👥 /members - Tags all group members (admins only, 8 at a time, 2-sec delay).")
        elif data == "help_rank":
            await query.edit_message_text("🏆 /rank - See the top chatterboxes in the group!")