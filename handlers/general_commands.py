# handlers/general_commands.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.group import chat_data, message_counts  # Import these from group.py

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    query = update.callback_query
    
    if not query or query.data == "help_back":
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
             InlineKeyboardButton("⚠️ Warn", callback_data="help_warn")],
            [InlineKeyboardButton("👢 Kick", callback_data="help_kick"),
             InlineKeyboardButton("😴 AFK", callback_data="help_afk")],
            [InlineKeyboardButton("🎉 Fun", callback_data="help_fun")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        help_text = (
            "Yo! I’m your slick bot! 😎\n"
            "Tap a button to see what I can do!\n\n"
            "Commands: /help, /info, /photo, /stat, /members, /top, /mute, /unmute, /active, /rank, /warn, /kick, /afk, /waifus..."
        )
        if query:
            await query.edit_message_text(text=help_text, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat.id, text=help_text, reply_markup=reply_markup)
    else:
        data = query.data
        summaries = {
            "help_info": "ℹ️ /info - Shows user PFP + dope details!",
            "help_photo": "📸 /photo - Grabs recent PFPs!",
            "help_stat": "📊 /stat - Leaderboard with top chatters!",
            "help_members": "👥 /members - Tags all members (admin only)!",
            "help_top": "🏆 /top - Top 3 chatterboxes!",
            "help_mute": "🔇 /mute - Mutes a user (admin only)!",
            "help_unmute": "🔊 /unmute - Unmutes a user (admin only)!",
            "help_active": "🌟 /active - Counts active users!",
            "help_rank": "🥇 /rank - Top 5 message senders!",
            "help_warn": "⚠️ /warn - Warns a user (admin only)!",
            "help_kick": "👢 /kick - Kicks a user (admin only)!",
            "help_afk": "😴 /afk - Mark yourself AFK with a custom message!"
        }
        if data in summaries:
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_back")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(summaries[data], reply_markup=reply_markup)
        elif data == "help_fun":
            fun_keyboard = [[InlineKeyboardButton(f"/{cmd}", callback_data=f"fun_{cmd}")] for cmd in FUN_COMMANDS.keys()]
            fun_keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="help_back")])
            reply_markup = InlineKeyboardMarkup(fun_keyboard)
            await query.edit_message_text("🎉 Fun Commands:\nRandom anime pics from waifu.pics!", reply_markup=reply_markup)
        elif data.startswith("fun_"):
            cmd = data.split("_")[1]
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_fun")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(f"/{cmd} - Fetches a random {cmd} image!", reply_markup=reply_markup)
        # ... (existing button logic)