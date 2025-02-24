from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from utils.helpers import get_user_photo, get_chat_photo
from datetime import datetime

async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    welcome_text = (
        f"🎉 *Boom! I’ve landed in {chat.title}!* 🎉\n"
        "Ready to shake things up with stats, moderation, and more.\n"
        "Type /help to unleash my powers!"
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=welcome_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    member_count = await context.bot.get_chat_member_count(chat.id)
    creation_date = datetime.fromtimestamp(chat.id / (1 << 32)).strftime('%Y-%m-%d')
    photo = await get_chat_photo(context.bot, chat.id)
    stats_text = (
        f"*Group: {chat.title}*\n"
        f"Members: {member_count}\n"
        f"Created: {creation_date} (approx)"
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=stats_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(stats_text, parse_mode="Markdown")

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        member = await context.bot.get_chat_member(chat.id, user.id)
        messages = "Unknown (API limit)"  # Placeholder for message count
        photo = await get_user_photo(context.bot, user.id)
        stat_text = (
            f"*Stats for {user.full_name}*\n"
            f"Username: @{user.username or 'None'}\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Total Messages: {messages}"
        )
    else:
        user = update.message.from_user
        member = await context.bot.get_chat_member(chat.id, user.id)
        messages = "Unknown (API limit)"  # Placeholder for message count
        photo = await get_user_photo(context.bot, user.id)
        stat_text = (
            f"*Your Stats, {user.full_name}!*\n"
            f"Username: @{user.username or 'None'}\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Total Messages: {messages}"
        )
    if photo:
        await update.message.reply_photo(photo=photo, caption=stat_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(stat_text, parse_mode="Markdown")

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"*Total members in {chat.title}:* {count}", parse_mode="Markdown")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption="*Top 5 users coming soon!* (Requires message tracking)", parse_mode="Markdown")
    else:
        await update.message.reply_text("*Top 5 users coming soon!* (Requires message tracking)", parse_mode="Markdown")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_restrict_members:
            await context.bot.restrict_chat_member(chat.id, user.id, permissions=ChatPermissions(can_send_messages=False))
            photo = await get_user_photo(context.bot, user.id)
            if photo:
                await update.message.reply_photo(photo=photo, caption=f"*Muted {user.full_name}!*", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"*Muted {user.full_name}!*", parse_mode="Markdown")
        else:
            await update.message.reply_text("*I need admin rights to mute users!*", parse_mode="Markdown")
    else:
        await update.message.reply_text("*Reply to a message with /mute to mute that user!*", parse_mode="Markdown")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        photos = await context.bot.get_user_profile_photos(user.id, limit=5)  # Get up to 5 past profile pics
        if photos.photos:
            for photo in photos.photos:
                await update.message.reply_photo(photo=photo[-1].file_id, caption=f"*Profile pic of {user.full_name}*", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"*No profile pics found for {user.full_name}!*", parse_mode="Markdown")
    else:
        user = update.message.from_user
        photos = await context.bot.get_user_profile_photos(user.id, limit=5)  # Get up to 5 past profile pics
        if photos.photos:
            for photo in photos.photos:
                await update.message.reply_photo(photo=photo[-1].file_id, caption=f"*Your profile pic, {user.full_name}*", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"*No profile pics found for you, {user.full_name}!*", parse_mode="Markdown")

async def active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    # Simulate active members (API doesn’t provide this directly)
    members = await context.bot.get_chat_administrators(chat.id)  # Example: Use admins as "active" for now
    active_text = "*🌟 Active Members in {chat.title} 🌟*\n\n"
    for member in members[:5]:  # Limit to 5 for brevity
        active_text += f"👤 {member.user.full_name} (@{member.user.username or 'No username'})\n"
    active_text += "\n*Note: Full activity tracking coming soon!*"
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption=active_text.format(chat=chat), parse_mode="Markdown")
    else:
        await update.message.reply_text(active_text.format(chat=chat), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    help_text = (
        "*Here’s what I can do in groups:*\n"
        "/start - Welcome message\n/stats - Group stats\n/stat - User stats (reply or self)\n"
        "/members - Member count\n/top - Top 5 users\n/mute - Toggle mute\n/photo - User profile pics\n"
        "/active - Active members\n/help - This list"
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=help_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")