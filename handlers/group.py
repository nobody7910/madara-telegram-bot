from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from utils.helpers import get_user_photo, get_chat_photo
from datetime import datetime
import random

async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    chat = update.message.chat
    bot_photo = await get_user_photo(bot, bot.id)  # Bot's profile pic
    intro_text = (
        f"🎉 *Greetings, {chat.title}!* 🎉\n"
        "I’m @Madara7_chat_bot, your group’s new MVP.\n"
        "Stats, ranks, and fun—ready to roll!"
    )
    keyboard = [
        [InlineKeyboardButton("Add me to another group", url=f"https://t.me/Madara7_chat_bot?startgroup=true")],
        [InlineKeyboardButton("Help", url=f"https://t.me/Madara7_chat_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if bot_photo:
        await update.message.reply_photo(photo=bot_photo, caption=intro_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(intro_text, parse_mode="Markdown", reply_markup=reply_markup)

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
        user_profile = await context.bot.get_user_profile_photos(user.id, limit=1)  # For bio (not directly available)
        bio = "Not available"  # Telegram API doesn’t provide bio directly
        messages = "Unknown (API limit)"  # Placeholder
        stat_text = (
            f"*Stats for {user.full_name}*\n"
            f"Username: @{user.username or 'None'}\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Bio: {bio}\n"
            f"Handle: @{user.username or 'No username'}"
        )
    else:
        user = update.message.from_user
        member = await context.bot.get_chat_member(chat.id, user.id)
        bio = "Not available"  # Placeholder
        messages = "Unknown (API limit)"  # Placeholder
        stat_text = (
            f"*Your Stats, {user.full_name}!*\n"
            f"Username: @{user.username or 'None'}\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Bio: {bio}\n"
            f"Handle: @{user.username or 'No username'}"
        )
    photo = await get_user_photo(context.bot, user.id)
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
    members = await context.bot.get_chat_administrators(chat.id)  # Use admins as proxy
    random.shuffle(members)  # Randomize for simulation
    top_text = f"*🏆 Top Members in {chat.title} 🏆*\n\n"
    for i, member in enumerate(members[:5], 1):  # Top 5
        top_text += f"{i}. {member.user.full_name} (@{member.user.username or 'No username'}) - Messages: {random.randint(50, 200)}\n"
    top_text += "\n*Note: Message counts are simulated until tracking is added!*"
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption=top_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(top_text, parse_mode="Markdown")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    user = update.message.from_user
    caller = await context.bot.get_chat_member(chat.id, user.id)
    if not (caller.status in ["administrator", "creator"]):
        await update.message.reply_text("*Only admins can use /mute@Madara7_chat_bot!*", parse_mode="Markdown")
        return
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_restrict_members:
            await context.bot.restrict_chat_member(chat.id, target_user.id, permissions=ChatPermissions(can_send_messages=False))
            photo = await get_user_photo(context.bot, target_user.id)
            if photo:
                await update.message.reply_photo(photo=photo, caption=f"*Muted {target_user.full_name}!*", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"*Muted {target_user.full_name}!*", parse_mode="Markdown")
        else:
            await update.message.reply_text("*I need admin rights to mute users!*", parse_mode="Markdown")
    else:
        await update.message.reply_text("*Reply to a message with /mute@Madara7_chat_bot to mute that user!*", parse_mode="Markdown")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    user = update.message.from_user
    caller = await context.bot.get_chat_member(chat.id, user.id)
    if not (caller.status in ["administrator", "creator"]):
        await update.message.reply_text("*Only admins can use /unmute@Madara7_chat_bot!*", parse_mode="Markdown")
        return
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_restrict_members:
            await context.bot.restrict_chat_member(chat.id, target_user.id, permissions=ChatPermissions(can_send_messages=True))
            photo = await get_user_photo(context.bot, target_user.id)
            if photo:
                await update.message.reply_photo(photo=photo, caption=f"*Unmuted {target_user.full_name}!*", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"*Unmuted {target_user.full_name}!*", parse_mode="Markdown")
        else:
            await update.message.reply_text("*I need admin rights to unmute users!*", parse_mode="Markdown")
    else:
        await update.message.reply_text("*Reply to a message with /unmute@Madara7_chat_bot to unmute that user!*", parse_mode="Markdown")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        photos = await context.bot.get_user_profile_photos(user.id, limit=5)
        if photos.photos:
            for photo in photos.photos:
                await update.message.reply_photo(photo=photo[-1].file_id, caption=f"*Profile pic of {user.full_name}*", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"*No profile pics found for {user.full_name}!*", parse_mode="Markdown")
    else:
        user = update.message.from_user
        photos = await context.bot.get_user_profile_photos(user.id, limit=5)
        if photos.photos:
            for photo in photos.photos:
                await update.message.reply_photo(photo=photo[-1].file_id, caption=f"*Your profile pic, {user.full_name}*", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"*No profile pics found for you, {user.full_name}!*", parse_mode="Markdown")

async def active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    members = await context.bot.get_chat_administrators(chat.id)  # Use admins as proxy
    random.shuffle(members)  # Randomize for simulation
    active_text = f"*🌟 Top 3 Active Members in {chat.title} 🌟*\n"
    active_text += "----------------------------------------\n"
    for i, member in enumerate(members[:3], 1):
        active_text += f"#{i} | {member.user.full_name} (@{member.user.username or 'No username'}) | Msgs: {random.randint(20, 100)}\n"
    active_text += "----------------------------------------\n"
    active_text += "*Note: Based on simulated activity until tracking is added!*"
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption=active_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(active_text, parse_mode="Markdown")

async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    members = await context.bot.get_chat_member_count(chat.id)
    if members > 1:
        random_member = await context.bot.get_chat_member(chat.id, random.choice(await context.bot.get_chat_administrators(chat.id)).user.id)
        rank_text = (
            f"*🎲 Random Rank in {chat.title} 🎲*\n"
            f"Member: {random_member.user.full_name} (@{random_member.user.username or 'No username'})\n"
            f"Rank: #{random.randint(1, members)}\n"
            f"Status: {random_member.status}\n"
            f"Messages: {random.randint(10, 150)} (simulated)"
        )
        photo = await get_user_photo(context.bot, random_member.user.id)
        if photo:
            await update.message.reply_photo(photo=photo, caption=rank_text, parse_mode="Markdown")
        else:
            await update.message.reply_text(rank_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("*Not enough members to rank!*", parse_mode="Markdown")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    photo = await get_chat_photo(context.bot, chat.id)
    bio = chat.description or "No bio set"
    if chat.type == "group" and chat.username:  # Public group
        invite_link = f"https://t.me/{chat.username}"
    else:  # Private group
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_invite_users:
            invite_link = await context.bot.create_chat_invite_link(chat.id, name=f"Invite to {chat.title}")
            invite_link = invite_link.invite_link
        else:
            invite_link = "I need admin rights to generate an invite link!"
    info_text = (
        f"*Info for {chat.title}*\n"
        f"Bio: {bio}\n"
        f"Invite Link: {invite_link}"
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=info_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(info_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    user = update.message.from_user
    help_text = (
        f"*Hey {user.full_name}!*\n"
        "Want the full scoop on my commands? Hit the button below to check them out in my PM!"
    )
    keyboard = [[InlineKeyboardButton("Command Details", url=f"https://t.me/Madara7_chat_bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption=help_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=reply_markup)