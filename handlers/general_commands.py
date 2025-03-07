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
    query = update.callback_query
    is_callback = bool(query)
    
    if not is_callback:  # Initial /help command
        keyboard = [
            [InlineKeyboardButton("ℹ️ Info", callback_data="help_info"),
             InlineKeyboardButton("📸 Photo", callback_data="help_photo")],
            [InlineKeyboardButton("📊 Stat", callback_data="help_stat"),
             InlineKeyboardButton("👥 Members", callback_data="help_members")],
            [InlineKeyboardButton("🏆 Top", callback_data="help_top"),
             InlineKeyboardButton("🔇 Mute", callback_data="help_mute")],
            [InlineKeyboardButton("🔊 Unmute", callback_data="help_unmute"),
             InlineKeyboardButton("🌟 Active", callback_data="help_active")],
            [InlineKeyboardButton("🥇 Rank", callback_data="help_rank"),
             InlineKeyboardButton("📈 Stats", callback_data="help_stats")],
            [InlineKeyboardButton("🚀 Start", callback_data="help_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot_photos = await context.bot.get_user_profile_photos(context.bot.id, limit=1)
        help_text = (
            "Hey there! I’m your cool bot! 😎\n"
            "Click a button to see what I can do!\n\n"
            "Commands: /help, /info, /start, /stats, /stat, /members, /top, /mute, /photo, /active, /unmute, /rank"
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
    else:  # Handle button clicks
        data = query.data
        summaries = {
            "help_info": "ℹ️ /info - Get dope info about a user, including their bio!",
            "help_photo": "📸 /photo - Snag recent PFPs of yourself or a replied user!",
            "help_stat": "📊 /stat - Shows group message stats (today, yesterday, monthly).",
            "help_members": "👥 /members [msg] - Tags all group members with an optional message (admins only).",
            "help_top": "🏆 /top - Lists the top 3 chatterboxes in the group!",
            "help_mute": "🔇 /mute - Silence someone (admins only, sassy if targeting an admin)!",
            "help_unmute": "🔊 /unmute - Free someone from mute (admins only)!",
            "help_active": "🌟 /active - Coming soon: Shows recently active users!",
            "help_rank": "🥇 /rank - Ranks top 5 message senders in the group!",
            "help_stats": "📈 /stats - Alias for /stat, group message stats!",
            "help_start": "🚀 /start - Kick off with your PFP and a fun intro!"
        }
        if data in summaries:
            await query.edit_message_text(summaries[data])