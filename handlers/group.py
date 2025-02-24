from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from utils.helpers import get_user_photo, get_chat_photo
from datetime import datetime
import random

async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    chat = update.message.chat
    bot_photo = await get_user_photo(bot, bot.id)  # Get bot's profile pic
    intro_text = (
        f"🎉 *Greetings, {chat.title}!* 🎉\n"
        "I’m @Madara7_chat_bot, your group’s new MVP.\n"
        "Stats, ranks, and fun—type /help@Madara7_chat_bot to see what I can do!"
    )
    if bot_photo:
        await update.message.reply_photo(photo=bot_photo, caption=intro_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(intro_text, parse_mode="Markdown")

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
        messages = "Unknown (API limit)"  # Placeholder
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
        messages = "Unknown (API limit)"  # Placeholder
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
    # Simulate top members
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
        await update.message.reply_text("*Reply to a message with /mute@Madara7_chat_bot to mute that user!*", parse_mode="Markdown")

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
    # Simulate top 3 active members
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
    # Randomly rank a member
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    user = update.message.from_user
    help_text = (
        f"*Hey {user.full_name}!*\n"
        "Want to know my powers? Check your PM for the full command list!"
    )
    keyboard = [[InlineKeyboardButton("See Commands in PM", url=f"https://t.me/Madara7_chat_bot?start=help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    photo = await get_chat_photo(context.bot, chat.id)
    if photo:
        await update.message.reply_photo(photo=photo, caption=help_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=reply_markup)