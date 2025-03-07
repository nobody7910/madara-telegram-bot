# handlers/general_commands.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    
    photos = await context.bot.get_user_profile_photos(user.id, limit=1)
    intro = (
        f"🎉 Yo yo, {user.first_name}! Welcome to the party! 🎉\n"
        "I’m your friendly neighborhood bot—hit /help for the rundown!"
    )
    
    if photos.photos:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=photos.photos[0][-1].file_id,
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
             InlineKeyboardButton("⚠️ Warn", callback_data="help_warn")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot_photos = await context.bot.get_user_profile_photos(context.bot.id, limit=1)
        help_text = (
            "Yo! I’m your slick bot! 😎\n"
            "Tap a button to see what I can do!\n\n"
            "Commands: /help, /info, /photo, /stat, /members, /top, /mute, /unmute, /active, /rank, /warn"
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
            "help_info": "ℹ️ /info - Drops a slick profile card with PFP, bio, and more!",
            "help_photo": "📸 /photo - Shows up to 3 recent PFPs of you or a replied user!",
            "help_stat": "📊 /stat - Group stats with PFP—today, yesterday, monthly vibes!",
            "help_members": "👥 /members [msg] - Tags all members (8 per msg, 2-sec delay) with a shoutout (admins only)!",
            "help_top": "🏆 /top - Top 3 chatterboxes in the group!",
            "help_mute": "🔇 /mute - Mutes a user (admins only, sassy if it’s an admin)!",
            "help_unmute": "🔊 /unmute - Unmutes a user (admins only)!",
            "help_active": "🌟 /active - Counts active users in the last 24 hours!",
            "help_rank": "🥇 /rank - Ranks top 5 message senders!",
            "help_warn": "⚠️ /warn - Warns a user (admins only, 3 strikes = ban)!"
        }
        if data in summaries:
            await query.edit_message_text(text=summaries[data], reply_markup=None)
        else:
            await query.answer("Something went wonky—try again!")