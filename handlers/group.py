# handlers/group.py
import logging
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from telegram.error import Forbidden, TelegramError
from PIL import Image, ImageDraw, ImageFont
import os
import re
from utils.db import get_db

logger = logging.getLogger(__name__)

# Initialize MongoDB collections
db = get_db()
message_counts = db.get_collection('message_counts')
chat_data = db.get_collection('chat_data')
warnings = db.get_collection('warnings')
afk_users = db.get_collection('afk_users')
tagging_operations = {}  # Keep this in-memory for simplicity

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(chat.id)
    user_id = str(user.id)
    today = datetime.now().date().isoformat()
    
    # Update message counts in MongoDB
    message_counts.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        {
            '$inc': {f'daily.{today}': 1, 'monthly': 1},
            '$set': {'last_seen': datetime.now().isoformat()}
        },
        upsert=True
    )
    
    # Update chat data in MongoDB
    admins = await chat.get_administrators()
    chat_data.update_one(
        {'chat_id': chat_id},
        {
            '$set': {
                'title': chat.title,
                'description': chat.description,
                'member_count': await chat.get_member_count(),
                'admins': [admin.user.id for admin in admins]
            }
        },
        upsert=True
    )
    
    # Check AFK status
    afk_record = afk_users.find_one({'chat_id': chat_id, 'user_id': user_id})
    if afk_record:
        afk_time = datetime.fromisoformat(afk_record['time'])
        duration = (datetime.now() - afk_time).total_seconds() // 60
        await update.message.reply_text(
            f"🎉 Welcome back, {user.first_name}! You were AFK for {duration} mins.\n"
            f"Last AFK reason: {afk_record['message']}"
        )
        afk_users.delete_one({'chat_id': chat_id, 'user_id': user_id})

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return
    
    new_members = update.message.new_chat_members
    for member in new_members:
        photos = await context.bot.get_user_profile_photos(member.id, limit=1)
        member_link = f"tg://user?id={member.id}"  # Use a simple user ID link to avoid issues
        # Escape special characters in first_name to prevent Markdown issues
        first_name_safe = member.first_name.replace("[", "\\[").replace("]", "\\]")
        username_safe = member.username if member.username else "N/A"
        welcome_text = (
            f"🎉 Woohoo! A wild {first_name_safe} has joined the party! 🎉\n"
            f"Get ready for some epic vibes in *{chat.title}*! 🌟\n\n"
            f"👤 Name: [{first_name_safe}]({member_link})\n"
            f"📛 Username: @{username_safe}\n"
            f"🆔 ID: {member.id}\n"
            f"Let’s make it legendary—follow the rules and enjoy! ☘️"
        )
        keyboard = [[InlineKeyboardButton("📜 Group Rules", url="https://t.me/RULES_FOR_GROUPS_791/3")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if photos.photos:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=photos.photos[0][-1].file_id,
                caption=welcome_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=chat.id,
                text=welcome_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user if not message.reply_to_message else message.reply_to_message.from_user
    
    try:
        user_info = await context.bot.get_chat(user.id)
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        bio = user_info.bio if user_info.bio else "No bio set—mysterious, huh?"
        photo_count = (await context.bot.get_user_profile_photos(user.id)).total_count
        
        info_text = (
            f"【 User Information 】\n"
            f"➢ ID: {user.id}\n"
            f"➢ First Name: {user.first_name}\n"
            f"➢ Last Name: {user.last_name if user.last_name else 'N/A'}\n"
            f"➢ Username: @{user.username if user.username else 'N/A'}\n"
            f"➢ Mention: {user.first_name}\n"
            f"➢ DC ID: N/A\n"
            f"➢ Bio: {bio}\n\n"
            f"➢ Custom Bio: N/A\n"
            f"➢ Custom Tag: N/A\n"
            f"➢ Profile Photos: {photo_count}\n"
            f"➢ Health: 100%\n"
            f"    ▰▰▰▰▰▰▰▰▰▰"
        )
        
        if photos.photos:
            await message.reply_photo(
                photo=photos.photos[0][-1].file_id,
                caption=info_text
            )
        else:
            await message.reply_text(info_text)
    except TelegramError as e:
        await message.reply_text(f"Couldn’t fetch info for {user.first_name}: {e}")

async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Yo, this only works in groups!")
        return
    
    chat_id = int(chat.id)
    await generate_leaderboard(update, context, chat_id, "all")

async def generate_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, period: str) -> None:
    now = datetime.now()
    if period == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "yesterday":
        start_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
    elif period == "month":
        start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_time = datetime(1970, 1, 1)

    users = []
    total_msgs = 0
    active_count = 0
    chat_id_str = str(chat_id)
    
    # Fetch message counts from MongoDB
    chat_records = message_counts.find({'chat_id': chat_id_str})
    chat_records_list = list(chat_records)
    if not chat_records_list:
        if update.callback_query:
            await update.callback_query.message.reply_text("No stats yet! Start chatting!")
        else:
            await update.message.reply_text("No stats yet! Start chatting!")
        return
    
    admins = await context.bot.get_chat_administrators(chat_id)
    admin_count = len(admins)
    
    for record in chat_records_list:
        user_id = record['user_id']
        try:
            user = await context.bot.get_chat_member(chat_id, int(user_id))
            username = user.user.username or user.user.first_name  # Still needed for image
            link = f"https://t.me/{user.user.username}" if user.user.username else ""  # Keep for fallback
            daily = record.get('daily', {})
            if period == "today":
                count = daily.get(start_time.date().isoformat(), 0)
            elif period == "yesterday":
                count = daily.get(start_time.date().isoformat(), 0)
            elif period == "month":
                count = sum(
                    count for date, count in daily.items()
                    if datetime.fromisoformat(date).date() >= start_time.date()
                )
            else:
                count = record.get('monthly', 0)
            if count > 0:
                users.append((username, link, count, user.user.first_name, user.user.id))  # Add first_name and id
                total_msgs += count
            last_seen = record.get('last_seen')
            if last_seen and (now - datetime.fromisoformat(last_seen)) <= timedelta(hours=24):
                active_count += 1
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
    
    if not users:
        if update.callback_query:
            await update.callback_query.message.reply_text(f"No messages found for {period}!")
        else:
            await update.message.reply_text(f"No messages found for {period}!")
        return
    
    users = sorted(users, key=lambda x: x[2], reverse=True)[:10]

    # Generate Image (unchanged)
    img = Image.new('RGB', (1000, 600), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    
    draw.ellipse((50, 50, 150, 150), fill=(139, 0, 0, 50))
    draw.ellipse((850, 450, 950, 550), fill=(139, 0, 0, 50))
    
    try:
        font_title = ImageFont.truetype("DejaVuSans.ttf", 60)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 30)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    draw.text((400, 20), "LEADERBOARD".upper(), font=font_title, fill=(255, 255, 255))

    bar_height = 40
    y_start = 100
    max_count = max(users, key=lambda x: x[2])[2]
    bar_color = (255, 99, 71)

    for i, (username, link, count, first_name, user_id) in enumerate(users, 1):
        bar_width = int((count / max_count) * 800) if max_count > 0 else 0
        y = y_start + (i - 1) * (bar_height + 10)
        draw.rectangle([100, y, 100 + bar_width, y + bar_height], fill=bar_color)
        draw.text((110, y), f"{i}. {username} • {count}", font=font_text, fill=(255, 255, 255))

    img.save("leaderboard.png")

    # Updated Caption with First Name and tg://user?id= link
    caption = f"*📈 {period.capitalize()} Leaderboard 📈*\n\n"
    caption += "🏆 *Top Chatters:*\n"
    for i, (username, link, count, first_name, user_id) in enumerate(users, 1):
        emoji = "👤" if i == 1 else "👤"
        caption += f"{i}. {emoji} [{first_name}](tg://user?id={user_id}) • {count} msgs\n"
    caption += f"\n✉️ *Total Messages:* {total_msgs}"

    keyboard = [
        [InlineKeyboardButton("Today", callback_data=f"stat_today_{chat_id}"),
         InlineKeyboardButton("Yesterday", callback_data=f"stat_yesterday_{chat_id}"),
         InlineKeyboardButton("Month", callback_data=f"stat_month_{chat_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("leaderboard.png", "rb") as photo:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command works only in groups!")
        return
    
    admins = await chat.get_administrators()
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:
        keyboard = [[InlineKeyboardButton("Grant Permissions", url=f"https://t.me/{context.bot.username}?start=permissions_{chat.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("I need an admin post to do these things!", reply_markup=reply_markup)
        return
    
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can kick people, bro! 😛")
        return
    
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif context.args and re.match(r'^@[\w]+$', context.args[0]):
        username = context.args[0][1:]  # Remove the @ symbol
        try:
            target = (await context.bot.get_chat_member(chat.id, username)).user
        except TelegramError:
            await message.reply_text(f"Couldn’t find {context.args[0]} in this group!")
            return
    
    if not target:
        await message.reply_text("Reply to someone or use /kick @username to kick them!")
        return
    
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Yo {user.first_name}, kicking an admin like {target.first_name}? That’s a no-go! 😂"
        )
        return
    
    try:
        await chat.ban_member(target.id)
        await chat.unban_member(target.id)
        await message.reply_text(f"👢 {target.first_name} got the boot! See ya! 👋")
    except TelegramError as e:
        await message.reply_text(f"Couldn’t kick {target.first_name}: {e}")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command works only in groups!")
        return
    
    admins = await chat.get_administrators()
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:
        keyboard = [[InlineKeyboardButton("Grant Permissions", url=f"https://t.me/{context.bot.username}?start=permissions_{chat.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("I need an admin post to do these things!", reply_markup=reply_markup)
        return
    
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can mute people, punk! 😛")
        return
    
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif context.args and re.match(r'^@[\w]+$', context.args[0]):
        username = context.args[0][1:]  # Remove the @ symbol
        try:
            target = (await context.bot.get_chat_member(chat.id, username)).user
        except TelegramError:
            await message.reply_text(f"Couldn’t find {context.args[0]} in this group!")
            return
    
    if not target:
        await message.reply_text("Reply to someone or use /mute @username to mute them, genius!")
        return
    
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Hey {user.first_name}, you stupid? You think I’m gonna mute an admin like {target.first_name}? 😂"
        )
    else:
        await chat.restrict_member(target.id, permissions={"can_send_messages": False})
        await message.reply_text(f"🔇 {target.first_name} has been muted! Silence is golden! 🤫")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command only works in groups!")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to unmute them!")
        return
    
    target = update.message.reply_to_message.from_user
    
    # Check if target is an admin
    admins = await chat.get_administrators()
    if any(admin.user.id == target.id for admin in admins):
        await update.message.reply_text(f"{target.first_name} is an admin—they’re already free to chat! 😛")
        return
    
    try:
        await chat.restrict_member(target.id, permissions={"can_send_messages": True})
        await update.message.reply_text(f"{target.first_name} has been unmuted! 🗣️")
    except TelegramError as e:
        logger.error(f"Failed to unmute {target.id}: {e}")
        await update.message.reply_text(f"Couldn’t unmute {target.first_name}. Error: {e.message}")

async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command works only in groups!")
        return
    
    admins = await chat.get_administrators()
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:
        keyboard = [[InlineKeyboardButton("Grant Permissions", url=f"https://t.me/{context.bot.username}?start=permissions_{chat.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("I need an admin post to do these things!", reply_markup=reply_markup)
        return
    
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can warn people, dude! 😛")
        return
    
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif context.args and re.match(r'^@[\w]+$', context.args[0]):
        username = context.args[0][1:]  # Remove the @ symbol
        try:
            target = (await context.bot.get_chat_member(chat.id, username)).user
        except TelegramError:
            await message.reply_text(f"Couldn’t find {context.args[0]} in this group!")
            return
    
    if not target:
        await message.reply_text("Reply to someone or use /warn @username to warn them!")
        return
    
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Yo {user.first_name}, warning an admin like {target.first_name}? Nah, that’s a bold move I won’t touch! 😂"
        )
        return
    
    chat_id = str(chat.id)
    user_id = str(target.id)
    
    # Update warnings in MongoDB
    warnings.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        {'$inc': {'count': 1}},
        upsert=True
    )
    warn_record = warnings.find_one({'chat_id': chat_id, 'user_id': user_id})
    warn_count = warn_record['count']
    
    if warn_count >= 3:
        try:
            await chat.ban_member(target.id)
            await message.reply_text(f"⚠️ {target.first_name} hit 3 warnings—bam, banned! 👋")
            warnings.delete_one({'chat_id': chat_id, 'user_id': user_id})
        except TelegramError as e:
            await message.reply_text(f"Couldn’t ban {target.first_name}: {e}")
    else:
        await message.reply_text(
            f"⚠️ {target.first_name}, you’ve been warned! {warn_count}/3 strikes—shape up or ship out!"
        )

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command works only in groups!")
        return
    
    admins = await chat.get_administrators()
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:
        keyboard = [[InlineKeyboardButton("Grant Permissions", url=f"https://t.me/{context.bot.username}?start=permissions_{chat.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("I need an admin post to do these things!", reply_markup=reply_markup)
        return
    
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can ban people, bro! 😛")
        return
    
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif context.args and re.match(r'^@[\w]+$', context.args[0]):
        username = context.args[0][1:]  # Remove the @ symbol
        try:
            chat_member = await context.bot.get_chat_member(chat.id, username)
            target = chat_member.user
        except TelegramError:
            await message.reply_text(f"Couldn’t find {context.args[0]} in this group!")
            return
    
    if not target:
        await message.reply_text("Reply to someone or use /ban @username to ban them!")
        return
    
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Yo {user.first_name}, banning an admin like {target.first_name}? That’s a no-go! 😂"
        )
        return
    
    target_link = f"https://t.me/{target.username}" if target.username else f"tg://user?id={target.id}"
    try:
        await chat.ban_member(target.id)
        await message.reply_text(
            f"🚫 **BAN HAMMER DROPPED!** 🚫\n"
            f"The notorious [{target.first_name}]({target_link}) has been banished from *{chat.title}*!\n"
            f"👉 Farewell, troublemaker! 👋\n"
            f"🎉 Group is safe again! 🌟"
            , parse_mode="Markdown"
        )
    except TelegramError as e:
        await message.reply_text(f"Couldn’t ban {target.first_name}: {e}")

async def members_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("Yo, this command is for groups only! Try it there! 😉")
        return
    
    admins = await chat.get_administrators()
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:
        keyboard = [[InlineKeyboardButton("Grant Permissions", url=f"https://t.me/{context.bot.username}?start=permissions_{chat.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("I need an admin post to do these things!", reply_markup=reply_markup)
        return
    
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can summon the crew with /members! 😛")
        return
    
    custom_msg = " ".join(context.args) if context.args else "hey"
    user_link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    init_message = (
        f"Tag Operation is started by [{user.first_name}]({user_link}). "
        f"You can use /cancel@Madara7_chat_bot Command to Cancel the process. "
        f"Have a nice chat!"
    )
    await message.reply_text(init_message, parse_mode="Markdown")
    
    chat_id = str(chat.id)
    tagging_operations[chat_id] = True
    
    try:
        member_count = await context.bot.get_chat_member_count(chat.id)
        if member_count == 0:
            await message.reply_text("No members to tag? This group’s a ghost town! 👻")
            del tagging_operations[chat_id]
            return
        
        # Use message_counts from MongoDB to tag active users
        active_users = message_counts.find({'chat_id': chat_id, 'monthly': {'$gt': 0}})
        member_list = []
        for record in active_users.limit(50):  # Limit to 50 for testing
            try:
                member = await context.bot.get_chat_member(chat.id, int(record['user_id']))
                member_list.append(member.user)
            except TelegramError:
                continue
        
        if not member_list:
            await message.reply_text("No active members to tag! Start chatting! 👻")
            del tagging_operations[chat_id]
            return
        
        for i in range(0, len(member_list), 8):
            batch = member_list[i:i+8]
            batch_tags = ", ".join(f"[{m.first_name}](https://t.me/{m.username if m.username else ''} or tg://user?id={m.id})" for m in batch)
            await context.bot.send_message(chat_id=chat.id, text=f"{custom_msg} {batch_tags}", parse_mode="Markdown")
            if i + 8 < len(member_list) and chat_id in tagging_operations:
                time.sleep(2)
            else:
                break
    except Forbidden:
        await message.reply_text("Can’t tag some folks—check my permissions!")
    except TelegramError as e:
        await message.reply_text(f"Oops, something went wrong: {e}")
    finally:
        if chat_id in tagging_operations:
            del tagging_operations[chat_id]

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    user_link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    
    if chat_id in tagging_operations and tagging_operations[chat_id]:
        del tagging_operations[chat_id]
        await message.reply_text(
            f"[{user.first_name}]({user_link}) The operation is stopped... Enjoy the peace!",
            parse_mode="Markdown"
        )
    else:
        await message.reply_text(
            f"{user.first_name} There is no operation to be paused right now. 🙄"
        )

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    ranked = message_counts.find({'chat_id': chat_id}).sort('monthly', -1).limit(5)
    ranked_list = list(ranked)  # Convert Cursor to list
    if not ranked_list:  # Check if list is empty
        await update.message.reply_text("No chatter yet! Start talking to climb the ranks! 😛")
        return
    
    rank_text = f"🏆 Top Chatterboxes in {chat.title} 🏆\n"
    for i, record in enumerate(ranked_list, 1):
        user_id = record['user_id']
        try:
            member = await chat.get_member(int(user_id))
            rank_text += f"{i}. {member.user.full_name} - {record['monthly']} msgs\n"
        except TelegramError:
            rank_text += f"{i}. User {user_id} - {record['monthly']} msgs (Gone?)\n"
    await update.message.reply_text(rank_text)

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    ranked = message_counts.find({'chat_id': chat_id}).sort('monthly', -1).limit(3)
    ranked_list = list(ranked)  # Convert Cursor to list
    if not ranked_list:  # Check if list is empty
        await update.message.reply_text("No top dogs yet! Chat more to claim the throne! 👑")
        return
    
    top_text = f"👑 Top monkeys in {chat.title} 👑\n"
    for i, record in enumerate(ranked_list, 1):
        user_id = record['user_id']
        try:
            member = await chat.get_member(int(user_id))
            top_text += f"{i}. {member.user.full_name} - {record['monthly']} msgs\n"
        except TelegramError:
            top_text += f"{i}. User {user_id} - {record['monthly']} msgs (Gone?)\n"
    await update.message.reply_text(top_text)

async def active_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    now = datetime.now()
    active_users = message_counts.find({
        'chat_id': chat_id,
        'last_seen': {'$gte': (now - timedelta(hours=24)).isoformat()}
    })
    active_users_list = list(active_users)  # Convert Cursor to list
    active_count = len(active_users_list)  # Count the list length
    chat_record = chat_data.find_one({'chat_id': chat_id})
    if not chat_record:
        await update.message.reply_text("No activity yet! Get chatting! 😛")
        return
    
    active_text = (
        f"🌟 Active Vibes in {chat.title} 🌟\n"
        f"Active Users (Last 24h): {active_count}\n"
        f"Total Members: {chat_record['member_count']}\n"
        f"Get in on the action! 😎"
    )
    await update.message.reply_text(active_text)

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await rank_command(update, context)

async def handle_stat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    if data.startswith("stat_"):
        period, chat_id = data.split("_")[1], int(data.split("_")[2])
        await generate_leaderboard(update, context, chat_id, period)
        await query.answer()

async def afk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Yo, AFK only works in groups!")
        return
    
    chat_id = str(chat.id)
    user_id = str(user.id)
    afk_msg = " ".join(context.args) or "AFK - Be right back!"
    if update.message.reply_to_message:
        afk_msg = update.message.reply_to_message.text
    
    # Update AFK status in MongoDB
    afk_users.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        {'$set': {'time': datetime.now().isoformat(), 'message': afk_msg}},
        upsert=True
    )
    await update.message.reply_text(f"✨ {user.first_name} is now AFK! Reason: {afk_msg}")