from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from utils.helpers import get_user_photo, get_chat_photo
from datetime import datetime, timedelta
import random
from message_tracker import get_message_counts  # Correct import from message_tracker.py

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
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if bot_photo:
        await update.message.reply_photo(photo=bot_photo, caption=intro_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(intro_text, parse_mode="Markdown", reply_markup=reply_markup)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    chat_id = chat.id
    user = update.message.from_user
    
    # Get message timestamps for this user in this chat
    message_data = get_message_counts(chat_id)
    if user.id in message_data:
        timestamps = message_data[user.id]
        now = datetime.now()
        
        # Calculate message counts for different time periods
        today = len([t for t in timestamps if t.date() == now.date()])
        yesterday = len([t for t in timestamps if t.date() == (now - timedelta(days=1)).date()])
        this_week = len([t for t in timestamps if t > now - timedelta(days=7)])
        this_month = len([t for t in timestamps if t > now - timedelta(days=30)])
        this_year = len([t for t in timestamps if t > now - timedelta(days=365)])
        
        photo = await get_user_photo(context.bot, user.id)
        stat_text = (
            f"*Here are the stats for {user.full_name}*\n"
            f"Username: @{user.username or 'None'}\n"
            f"ID: {user.id}\n"
            f"Messages Today: {today}\n"
            f"Messages Yesterday: {yesterday}\n"
            f"Messages This Week: {this_week}\n"
            f"Messages This Month: {this_month}\n"
            f"Messages This Year: {this_year}\n"
            "*Note:* Stats reset when I restart—keep chatting!"
        )
    else:
        photo = await get_user_photo(context.bot, user.id)
        stat_text = (
            f"*Here are the stats for {user.full_name}*\n"
            f"Username: @{user.username or 'None'}\n"
            f"ID: {user.id}\n"
            "No messages tracked yet—start chatting!"
        )
    
    if photo:
        await update.message.reply_photo(photo=photo, caption=stat_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(stat_text, parse_mode="Markdown")

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    await update.message.reply_text(
        f"*Soon and in construction!*\n"
        f"Please enjoy other commands in *{chat.title}*!",
        parse_mode="Markdown"
    )

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    chat_id = chat.id
    photo = await get_chat_photo(context.bot, chat_id)
    
    # Get message counts for this chat
    message_data = get_message_counts(chat_id)
    if message_data:
        ranked_users = sorted(message_data.items(), key=lambda x: len(x[1]), reverse=True)[:5]  # Top 5 by message count
        top_text = f"*🌟 Top 5 Active Members in {chat.title} 🌟*\n\n"
        top_text += "----------------------------------------\n"
        for i, (user_id, timestamps) in enumerate(ranked_users, 1):
            try:
                member = await context.bot.get_chat_member(chat_id, user_id)
                user = member.user
                top_text += f"#{i} | {user.full_name} (@{user.username or 'No username'}) | Messages: {len(timestamps)}\n"
            except:
                top_text += f"#{i} | Unknown User (ID: {user_id}) | Messages: {len(timestamps)}\n"
        top_text += "----------------------------------------\n"
        top_text += "\n*Note:* Rankings reset when I restart—keep the chat alive!"
    else:
        top_text = f"*No activity tracked in {chat.title} yet!*\nStart chatting to see the top 5!"
    
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
        target_member = await context.bot.get_chat_member(chat.id, target_user.id)
        if target_member.status in ["administrator", "creator"]:
            await update.message.reply_text(
                "*Ooo u stupid, I can’t mute an admin!*\n"
                "Even I, @Madara7_chat_bot, know better than to mess with the big shots!",
                parse_mode="Markdown"
            )
            return
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_restrict_members:
            await context.bot.restrict_chat_member(chat.id, target_user.id, permissions=ChatPermissions(can_send_messages=False))
            photo = await get_user_photo(context.bot, target_user.id)
            mute_text = (
                f"*Muted {target_user.full_name}!*\n"
                "Silence is golden, and I’ve just handed out some gold! 🎤✨"
            )
            if photo:
                await update.message.reply_photo(photo=photo, caption=mute_text, parse_mode="Markdown")
            else:
                await update.message.reply_text(mute_text, parse_mode="Markdown")
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
        target_member = await context.bot.get_chat_member(chat.id, target_user.id)
        if target_member.status in ["administrator", "creator"]:
            await update.message.reply_text(
                "*Ooo u silly goose, I can’t unmute an admin!*\n"
                "They’re too cool to be muted anyway! 😎",
                parse_mode="Markdown"
            )
            return
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.can_restrict_members:
            await context.bot.restrict_chat_member(chat.id, target_user.id, permissions=ChatPermissions(can_send_messages=True))
            photo = await get_user_photo(context.bot, target_user.id)
            unmute_text = (
                f"*Unmuted {target_user.full_name}!*\n"
                "The gag’s off—let the chatter begin anew! 🗣️🎉"
            )
            if photo:
                await update.message.reply_photo(photo=photo, caption=unmute_text, parse_mode="Markdown")
            else:
                await update.message.reply_text(unmute_text, parse_mode="Markdown")
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
    member_count = await context.bot.get_chat_member_count(chat.id)
    active_text = (
        f"*🌟 Activity Status of {chat.title} 🌟*\n"
        f"Total Members: {member_count}\n"
        f"Active Vibes: {random.randint(int(member_count * 0.5), member_count)} members buzzing around! (simulated)\n"
        "*Note:* Exact active counts aren’t available—enjoy the vibe check instead!"
    )
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
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        member = await context.bot.get_chat_member(chat.id, user.id)
        messages = "Unknown (API limit)"  # Placeholder
        bio = user.first_name  # Substitute since bio isn’t available via API
        stat_text = (
            f"*Stats for {user.full_name}*\n"
            f"Username: @{user.username or 'None'}\n"
            f"ID: {user.id}\n"
            f"Status: {member.status}\n"
            f"Messages: {messages}\n"
            f"Bio: {bio}"
        )
        photo = await get_user_photo(context.bot, user.id)
        if photo:
            await update.message.reply_photo(photo=photo, caption=stat_text, parse_mode="Markdown")
        else:
            await update.message.reply_text(stat_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("*Reply to a message with /info@Madara7_chat_bot to see that user’s stats!*", parse_mode="Markdown")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    chat_id = chat.id
    for new_member in update.message.new_chat_members:
        photo = await get_user_photo(context.bot, new_member.id)
        welcome_text = (
            f"*Welcome to {chat.title}, {new_member.full_name}!* 🎉\n"
            f"Username: @{new_member.username or 'None'}\n"
            f"ID: {new_member.id}\n"
            "Glad you’re here—let’s make some noise together! 🎊"
        )
        if photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=welcome_text, parse_mode="Markdown")
        else:
            await context.bot