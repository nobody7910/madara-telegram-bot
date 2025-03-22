import logging
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ChatMemberHandler, filters
from telegram.error import Forbidden, TelegramError
from PIL import Image, ImageDraw, ImageFont
import os
import re
from utils.db import get_db

logger = logging.getLogger(__name__)

# Track messages (fixed AFK break logic)
async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    if chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(chat.id)
    user_id = str(user.id)
    today = datetime.now().date().isoformat()
    
    db = get_db()
    message_counts = db.get_collection('message_counts')
    chat_data = db.get_collection('chat_data')
    afk_users = db.get_collection('afk_users')
    
    # Check AFK status first
    afk_record = afk_users.find_one({'chat_id': chat_id, 'user_id': user_id})
    if afk_record:
        afk_time = datetime.fromisoformat(afk_record['time'])
        duration = (datetime.now() - afk_time).total_seconds() // 60  # Duration in minutes
        afk_reason = afk_record.get('message', 'No reason provided')
        
        # Prepare the AFK break message
        break_message = (
            f"🎉 Welcome back, {user.first_name}! You were AFK for {int(duration)} mins.\n"
            f"Last AFK reason: "
        )
        
        # Handle different types of AFK reasons
        try:
            if afk_reason.startswith("Sticker:"):
                sticker_id = afk_reason.split("Sticker: ")[1]
                await message.reply_text(
                    break_message + "a sticker (see below)",
                    reply_to_message_id=message.message_id
                )
                await context.bot.send_sticker(chat_id=chat.id, sticker=sticker_id)
            elif afk_reason.startswith("GIF:"):
                gif_id = afk_reason.split("GIF: ")[1]
                await message.reply_text(
                    break_message + "a GIF (see below)",
                    reply_to_message_id=message.message_id
                )
                await context.bot.send_animation(chat_id=chat.id, animation=gif_id)
            else:
                await message.reply_text(
                    break_message + f"{afk_reason}",
                    reply_to_message_id=message.message_id
                )
        except TelegramError as e:
            logger.error(f"Error sending AFK break message: {e}")
        
        # Remove AFK status
        afk_users.delete_one({'chat_id': chat_id, 'user_id': user_id})
        logger.info(f"AFK status cleared for {user_id} in {chat_id}")
    
    # Update message count
    message_counts.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        {
            '$inc': {f'daily.{today}': 1, 'monthly': 1},
            '$set': {'last_seen': datetime.now().isoformat()}
        },
        upsert=True
    )
    
    # Update chat data
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

# Welcome new members (unchanged)
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return
    
    if update.message and update.message.new_chat_members:
        new_members = update.message.new_chat_members
    elif update.chat_member and update.chat_member.new_chat_member.status in [ChatMember.MEMBER]:
        new_members = [update.chat_member.new_chat_member.user]
    else:
        return
    
    for member in new_members:
        photos = await context.bot.get_user_profile_photos(member.id, limit=1)
        member_link = f"tg://user?id={member.id}"
        first_name_safe = member.first_name.replace("[", "\\[").replace("]", "\\]")
        username_safe = member.username if member.username else "N/A"
        welcome_text = (
            f"┏━━━━━━━━━━━━━━━━⧫\n"
            f"┠●🎉нєу вυ∂∂у ωєℓ¢σмє🌀🌸 \n" 
            f"┠● {first_name_safe} ʜᴀs ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴡᴏʀʟᴅ 🎉\n"
            f"┠● 🫧*{chat.title}*! 🌟\n"
            f"┠●👤 ғɪʀsᴛ ɴᴀᴍᴇ: [{first_name_safe}]({member_link})\n"
            f"┠●📛 ᴜsᴇʀɴᴀᴍᴇ: @{username_safe}\n"
            f"┠●🆔 ɪᴅ: {member.id}\n"
            f"┠● ʟᴇᴛs ᴍᴀᴋᴇ ᴀ ɢᴏᴏᴅ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ, \n"
            f"┠● ғᴏʟʟᴏᴡ ᴛʜᴇ ʀᴜʟᴇs 🔽 ☘️\n"
            f"┗━━━━━━━━━━━━━━━━⧫"
        )
        keyboard = [[InlineKeyboardButton("📜 ɢʀᴏᴜᴘ ʀᴜʟᴇs", url="https://t.me/RULES_FOR_GROUPS_791/3")]]
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

# Handle chat member updates (unchanged)
async def handle_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return

    old_status = update.chat_member.old_chat_member.status
    new_status = update.chat_member.new_chat_member.status
    member = update.chat_member.new_chat_member.user

    if member.is_bot:
        return

    if old_status in ["left", "kicked"] and new_status == "member":
        await welcome_new_member(update, context)

# Info command (unchanged)
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
            f"❖ ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ❖\n"
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

# Stat command and leaderboard generation (unchanged)
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
    
    db = get_db()
    message_counts = db.get_collection('message_counts')
    
    chat_records = list(message_counts.find({'chat_id': chat_id_str}))
    if not chat_records:
        if update.callback_query:
            await update.callback_query.message.reply_text("No stats yet! Start chatting!")
        else:
            await update.message.reply_text("No stats yet! Start chatting!")
        return
    
    admins = await context.bot.get_chat_administrators(chat_id)
    admin_count = len(admins)
    
    for record in chat_records:
        user_id = record['user_id']
        try:
            user = await context.bot.get_chat_member(chat_id, int(user_id))
            username = user.user.username or user.user.first_name
            link = f"https://t.me/{user.user.username}" if user.user.username else ""
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
                users.append((username, link, count, user.user.first_name, user.user.id))
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

    caption = f"*📈 {period.capitalize()} Leaderboard 📈*\n\n"
    caption += "🏆 *Top Chatters:*\n"
    for i, (username, link, count, first_name, user_id) in enumerate(users, 1):
        emoji = "👤" if i == 1 else "👤"
        caption += f"{i}. {emoji} [{first_name}](tg://user?id={user_id}) • {count} msgs\n"
    caption += f"\n✉️ *Total Messages:* {total_msgs}"
    if period in ["today", "yesterday", "month"]:
        caption += f"\nThis is your {period} stat of group"

    keyboard = [
        [
            InlineKeyboardButton("𝚃𝙾𝙳𝙰𝚈", callback_data=f"stat_today_{chat_id}"),
            InlineKeyboardButton("𝚈𝚎𝚜𝚝𝚎𝚛𝚍𝚊𝚈", callback_data=f"stat_yesterday_{chat_id}"),
            InlineKeyboardButton("𝙼𝙾𝙽𝚃𝙷", callback_data=f"stat_month_{chat_id}")
        ]
    ]
    if period != "all":
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"stat_all_{chat_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open("leaderboard.png", "rb") as photo:
        if update.callback_query:
            await update.callback_query.edit_message_caption(
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await update.callback_query.answer()
        else:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

# Kick command (unchanged)
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
        username = context.args[0][1:]
        try:
            chat_member = await context.bot.get_chat_member(chat.id, username)
            target = chat_member.user
        except TelegramError:
            await message.reply_text(f"Couldn’t find @{username} in this group!")
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

# Mute command (unchanged)
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
        username = context.args[0][1:]
        try:
            chat_member = await context.bot.get_chat_member(chat.id, username)
            target = chat_member.user
        except TelegramError:
            await message.reply_text(f"Couldn’t find @{username} in this group!")
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

# Unmute command (unchanged)
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command only works in groups!")
        return
    
    admins = await chat.get_administrators()
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:
        keyboard = [[InlineKeyboardButton("Grant Permissions", url=f"https://t.me/{context.bot.username}?start=permissions_{chat.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("I need an admin post to do these things!", reply_markup=reply_markup)
        return
    
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can unmute people, dude! 😛")
        return
    
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif context.args and re.match(r'^@[\w]+$', context.args[0]):
        username = context.args[0][1:]
        try:
            chat_member = await context.bot.get_chat_member(chat.id, username)
            target = chat_member.user
        except TelegramError:
            await message.reply_text(f"Couldn’t find @{username} in this group!")
            return
    
    if not target:
        await message.reply_text("Reply to someone or use /unmute @username to unmute them!")
        return
    
    try:
        await chat.restrict_member(target.id, permissions={"can_send_messages": True})
        await message.reply_text(f"🔊 {target.first_name} has been unmuted! 🗣️")
    except TelegramError as e:
        logger.error(f"Failed to unmute {target.id}: {e}")
        await message.reply_text(f"Couldn’t unmute {target.first_name}. Error: {e}")

# Warn command (unchanged)
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
        username = context.args[0][1:]
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
    
    db = get_db()
    warnings = db.get_collection('warnings')
    
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

# Ban command (unchanged)
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
        username = context.args[0][1:]
        try:
            chat_member = await context.bot.get_chat_member(chat.id, username)
            target = chat_member.user
        except TelegramError:
            await message.reply_text(f"Couldn’t find @{username} in this group!")
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

# Remaining commands (unchanged)
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
        
        db = get_db()
        message_counts = db.get_collection('message_counts')
        
        active_users = list(message_counts.find({'chat_id': chat_id, 'monthly': {'$gt': 0}}))
        member_list = []
        for record in active_users:
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
    
    db = get_db()
    message_counts = db.get_collection('message_counts')
    
    ranked = list(message_counts.find({'chat_id': chat_id}).sort('monthly', -1).limit(5))
    if not ranked:
        await update.message.reply_text("No chatter yet! Start talking to climb the ranks! 😛")
        return
    
    rank_text = f"🏆 𝚃𝚘𝚙 𝚌𝚑𝚊𝚝𝚝𝚎𝚛𝚋𝚘𝚡𝚎𝚜 𝚒𝚗 𝚝𝚑𝚎 𝚐𝚛𝚘𝚞𝚙 🫡🥸{chat.title} 🏆\n"
    for i, record in enumerate(ranked, 1):
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
    
    db = get_db()
    message_counts = db.get_collection('message_counts')
    
    ranked = list(message_counts.find({'chat_id': chat_id}).sort('monthly', -1).limit(3))
    if not ranked:
        await update.message.reply_text("No top dogs yet! Chat more to claim the throne! 👑")
        return
    
    top_text = f"👑 Top monkeys in {chat.title} 👑\n"
    for i, record in enumerate(ranked, 1):
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
    
    db = get_db()
    message_counts = db.get_collection('message_counts')
    chat_data = db.get_collection('chat_data')
    
    active_users = list(message_counts.find({
        'chat_id': chat_id,
        'last_seen': {'$gte': (now - timedelta(hours=24)).isoformat()}
    }))
    active_count = len(active_users)
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
        chat = update.effective_chat
        user = query.from_user

        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = {admin.user.id for admin in admins}
        if user.id not in admin_ids:
            await query.answer("Only group admins can use these buttons! 🔒", show_alert=True)
            return

        await generate_leaderboard(update, context, chat_id, period)
        await query.answer()

# AFK command (unchanged)
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
        reply_msg = update.message.reply_to_message
        if reply_msg.text:
            afk_msg = reply_msg.text
        elif reply_msg.sticker:
            afk_msg = f"Sticker: {reply_msg.sticker.file_id}"
        elif reply_msg.animation:
            afk_msg = f"GIF: {reply_msg.animation.file_id}"
    
    db = get_db()
    afk_users = db.get_collection('afk_users')
    
    afk_users.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        {'$set': {'time': datetime.now().isoformat(), 'message': afk_msg}},
        upsert=True
    )
    await update.message.reply_text(f"✨ {user.first_name} is now AFK! Reason: {afk_msg if not afk_msg.startswith(('Sticker:', 'GIF:')) else 'a sticker/GIF'}")

tagging_operations = {}