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
    
    if not query or query.data == "help_back":  # Initial /help or Back button
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
            [InlineKeyboardButton("👢 Kick", callback_data="help_kick")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        help_text = (
            "Yo! I’m your slick bot! 😎\n"
            "Tap a button to see what I can do!\n\n"
            "Commands: /help, /info, /photo, /stat, /members, /top, /mute, /unmute, /active, /rank, /warn, /kick"
        )
        if query:
            await query.edit_message_text(text=help_text, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat.id, text=help_text, reply_markup=reply_markup)
    else:  # Button click
        data = query.data
        summaries = {
            "help_info": "ℹ️ /info - Shows user PFP + dope details like ID, bio, and more!",
            "help_photo": "📸 /photo - Grabs up to 3 recent PFPs of you or a replied user!",
            "help_stat": "📊 /stat - Bot PFP + message stats (today, yesterday, monthly)!",
            "help_members": "👥 /members [msg] - Tags all members (8 per msg, 2-sec delay) with a shoutout (admins only)!",
            "help_top": "🏆 /top - Top 3 chatterboxes in the group!",
            "help_mute": "🔇 /mute - Mutes a user (admins only, sassy for admins)!",
            "help_unmute": "🔊 /unmute - Unmutes a user (admins only)!",
            "help_active": "🌟 /active - Counts active users in the last 24h!",
            "help_rank": "🥇 /rank - Ranks top 5 message senders!",
            "help_warn": "⚠️ /warn - Warns a user (admins only, 3 strikes = ban)!",
            "help_kick": "👢 /kick - Kicks a user out (admins only)!"
        }
        if data in summaries:
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_back")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(summaries[data], reply_markup=reply_markup)
        elif data == "add_to_group":
            # List all groups the user is in (where bot tracks messages)
            user = query.from_user
            user_groups = [chat for chat_id, chat in chat_data.items() if chat_id in message_counts and str(user.id) in message_counts[chat_id]]
            if not user_groups:
                await query.edit_message_text("I don’t see you in any groups I’m in! Add me manually with an invite link!")
                return
            
            keyboard = [[InlineKeyboardButton(group["title"], callback_data=f"invite_{chat_id}")] 
                       for chat_id, group in chat_data.items() if chat_id in message_counts and str(user.id) in message_counts[chat_id]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Pick a group to add me to:", reply_markup=reply_markup)
        elif data.startswith("invite_"):
            chat_id = data.split("_")[1]
            try:
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=int(chat_id),
                    member_limit=1,
                    name=f"Invite by {user.first_name}"
                )
                # Refresh the process with the original button
                keyboard = [[InlineKeyboardButton("Add me to a group", callback_data="add_to_group")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    text=f"Bot added! Here’s the invite link for {chat_data[chat_id]['title']}:\n{invite_link.invite_link}",
                    reply_markup=reply_markup
                )
            except TelegramError as e:
                await query.edit_message_text(f"Couldn’t create invite for {chat_data[chat_id]['title']}: {e}")
        else:
            await query.answer("Oops, something’s off—try again!")