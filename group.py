# handlers/group.py
import logging
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import Forbidden, TelegramError
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
import os

logger = logging.getLogger(__name__)

# In-memory storage
message_counts = {}
chat_data = {}
warnings = {}
afk_users = defaultdict(lambda: {"time": None, "message": None})

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        return
    
    chat_id = str(chat.id)
    user_id = str(user.id)
    today = datetime.now().date()
    
    if chat_id not in message_counts:
        message_counts[chat_id] = {}
    if user_id not in message_counts[chat_id]:
        message_counts[chat_id][user_id] = {"daily": {}, "monthly": 0, "last_seen": None}
    if today not in message_counts[chat_id][user_id]["daily"]:
        message_counts[chat_id][user_id]["daily"][today] = 0
    message_counts[chat_id][user_id]["daily"][today] += 1
    message_counts[chat_id][user_id]["monthly"] += 1
    message_counts[chat_id][user_id]["last_seen"] = datetime.now()
    
    if chat_id not in chat_data:
        chat_data[chat_id] = {
            "title": chat.title,
            "description": chat.description,
            "member_count": await chat.get_member_count(),
            "admins": [admin.user.id for admin in await chat.get_administrators()]
        }
    
    # AFK Check (integrated with your structure)
    if (int(chat_id), int(user_id)) in afk_users:
        afk_data = afk_users.pop((int(chat_id), int(user_id)))
        duration = (datetime.now() - afk_data["time"]).total_seconds() // 60
        await update.message.reply_text(
            f"🎉 Welcome back, {user.first_name}! You were AFK for {duration} mins.\n"
            f"Last AFK reason: {afk_data['message']}"
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
    
    chat_id = int(chat.id)  # Use int for consistency with callback
    await generate_leaderboard(update, context, chat_id, "all")

async def generate_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, period: str) -> None:
    # Filter messages by period
    now = datetime.now()
    if period == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "yesterday":
        start_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
    elif period == "month":
        start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # all
        start_time = datetime(1970, 1, 1)

    # Get top 10 users
    users = []
    total_msgs = 0
    chat_id_str = str(chat_id)
    if chat_id_str not in message_counts:
        await update.message.reply_text("No stats yet! Start chatting!")
        return
    
    for user_id, data in message_counts[chat_id_str].items():
        try:
            user = await context.bot.get_chat_member(chat_id, int(user_id))
            username = user.user.username or user.user.first_name
            link = f"https://t.me/{user.user.username}" if user.user.username else ""
            if period == "today":
                count = data["daily"].get(start_time.date(), 0)
            elif period == "yesterday":
                count = data["daily"].get(start_time.date(), 0)
            elif period == "month":
                count = sum(
                    count for date, count in data["daily"].items()
                    if date >= start_time.date()
                )
            else:  # all
                count = data["monthly"]
            if count > 0:  # Only include users with messages
                users.append((username, link, count))
                total_msgs += count
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
    
    if not users:
        await update.message.reply_text(f"No messages found for {period}!")
        return
    
    users = sorted(users, key=lambda x: x[2], reverse=True)[:10]

    # Generate image
    img = Image.new('RGB', (800, 600), color=(44, 47, 51))  # Dark background
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 24)  # Default font, adjust path if needed
    except:
        font = ImageFont.load_default()

    draw.text((20, 20), f"📈 LEADERBOARD ({period.capitalize()})", font=font, fill=(255, 215, 0))  # Gold title
    y = 80
    for i, (username, link, count) in enumerate(users, 1):
        emoji = "👤" if i > 2 else "👦🏻" if i == 2 else "👤"
        text = f"{i}. {emoji} {username} ({link or 'No link'}) • {count}"
        draw.text((20, y), text, font=font, fill=(255, 255, 255))
        y += 40
    
    draw.text((20, y + 20), f"✉️ Total messages: {total_msgs}", font=font, fill=(255, 255, 255))

    # Save image
    img.save("leaderboard.png")

    # Buttons
    keyboard = [
        [InlineKeyboardButton("Today", callback_data=f"stat_today_{chat_id}"),
         InlineKeyboardButton("Yesterday", callback_data=f"stat_yesterday_{chat_id}"),
         InlineKeyboardButton("Month", callback_data=f"stat_month_{chat_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send image
    with open("leaderboard.png", "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, reply_markup=reply_markup)

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
    
    if not message.reply_to_message:
        await message.reply_text("Reply to someone to kick them!")
        return
    
    target = message.reply_to_message.from_user
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Yo {user.first_name}, kicking an admin like {target.first_name}? That’s a no-go! 😂"
        )
        return
    
    try:
        await chat.ban_member(target.id)
        await chat.unban_member(target.id)  # Ban then unban = kick
        await message.reply_text(f"{target.first_name} got the boot! See ya! 👢")
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
    
    if not message.reply_to_message:
        await message.reply_text("Reply to someone to mute them, genius!")
        return
    
    target = message.reply_to_message.from_user
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Hey {user.first_name}, you stupid? You think I’m gonna mute an admin like {target.first_name}? 😂"
        )
    else:
        await chat.restrict_member(target.id, permissions={"can_send_messages": False})
        await message.reply_text(f"{target.first_name} has been muted! Silence is golden! 🤫")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        await message.reply_text("Only admins can unmute, buddy! 😛")
        return
    
    if not message.reply_to_message:
        await message.reply_text("Reply to someone to unmute them!")
        return
    
    target = message.reply_to_message.from_user
    await chat.restrict_member(target.id, permissions={"can_send_messages": True})
    await message.reply_text(f"{target.first_name} is free from the mute dungeon! Speak up, champ! 🎉")

async def members_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("Yo, this command is for groups only! Try it there! 😉")
        return
    
    admins = await chat.get_administrators()
    bot_member = await chat.get_member(context.bot.id)
    if not bot_member.can_restrict_members:  # Using as a proxy for general perms
        keyboard = [[InlineKeyboardButton("Grant Permissions", url=f"https://t.me/{context.bot.username}?start=permissions_{chat.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text("I need an admin post to do these things!", reply_markup=reply_markup)
        return
    
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can summon the crew with /members! 😛")
        return
    
    custom_msg = " ".join(context.args) if context.args else "Yo, assemble!"
    await message.reply_text(f"📢 Tagging all members! {custom_msg} 🔔")
    
    try:
        members = await chat.get_members()
        member_list = [m.user for m in members if not m.user.is_bot]
        if not member_list:
            await message.reply_text("No members to tag? This group’s a ghost town! 👻")
            return
        
        for i in range(0, len(member_list), 8):
            batch = member_list[i:i+8]
            tags = " ".join(f"@{m.username}" if m.username else m.first_name for m in batch)
            await context.bot.send_message(chat_id=chat.id, text=f"{custom_msg} {tags}")
            if i + 8 < len(member_list):
                time.sleep(2)
    except Forbidden:
        await message.reply_text("Can’t tag some folks—check my permissions!")
    except TelegramError as e:
        await message.reply_text(f"Oops, something went wrong: {e}")

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
    
    if not message.reply_to_message:
        await message.reply_text("Reply to someone to warn them!")
        return
    
    target = message.reply_to_message.from_user
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Yo {user.first_name}, warning an admin like {target.first_name}? Nah, that’s a bold move I won’t touch! 😂"
        )
        return
    
    chat_id = str(chat.id)
    user_id = str(target.id)
    if chat_id not in warnings:
        warnings[chat_id] = {}
    if user_id not in warnings[chat_id]:
        warnings[chat_id][user_id] = 0
    
    warnings[chat_id][user_id] += 1
    warn_count = warnings[chat_id][user_id]
    
    if warn_count >= 3:
        try:
            await chat.ban_member(target.id)
            await message.reply_text(f"{target.first_name} hit 3 warnings—bam, banned! 👋")
            del warnings[chat_id][user_id]
        except TelegramError as e:
            await message.reply_text(f"Couldn’t ban {target.first_name}: {e}")
    else:
        await message.reply_text(
            f"⚠️ {target.first_name}, you’ve been warned! {warn_count}/3 strikes—shape up or ship out!"
        )

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    if chat_id not in message_counts or not message_counts[chat_id]:
        await update.message.reply_text("No chatter yet! Start talking to climb the ranks! 😛")
        return
    
    ranked = sorted(message_counts[chat_id].items(), key=lambda x: x[1]["monthly"], reverse=True)[:5]
    rank_text = f"🏆 Top Chatterboxes in {chat.title} 🏆\n"
    for i, (user_id, data) in enumerate(ranked, 1):
        try:
            member = await chat.get_member(int(user_id))
            rank_text += f"{i}. {member.user.full_name} - {data['monthly']} msgs\n"
        except TelegramError:
            rank_text += f"{i}. User {user_id} - {data['monthly']} msgs (Gone?)\n"
    await update.message.reply_text(rank_text)

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    if chat_id not in message_counts or not message_counts[chat_id]:
        await update.message.reply_text("No top dogs yet! Chat more to claim the throne! 👑")
        return
    
    ranked = sorted(message_counts[chat_id].items(), key=lambda x: x[1]["monthly"], reverse=True)[:3]
    top_text = f"👑 Top Dogs in {chat.title} 👑\n"
    for i, (user_id, data) in enumerate(ranked, 1):
        try:
            member = await chat.get_member(int(user_id))
            top_text += f"{i}. {member.user.full_name} - {data['monthly']} msgs\n"
        except TelegramError:
            top_text += f"{i}. User {user_id} - {data['monthly']} msgs (Gone?)\n"
    await update.message.reply_text(top_text)

async def active_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    if chat_id not in message_counts or not message_counts[chat_id]:
        await update.message.reply_text("No activity yet! Get chatting! 😛")
        return
    
    now = datetime.now()
    active_users = [
        (user_id, data) for user_id, data in message_counts[chat_id].items()
        if data["last_seen"] and (now - data["last_seen"]) <= timedelta(hours=24)
    ]
    active_count = len(active_users)
    active_text = (
        f"🌟 Active Vibes in {chat.title} 🌟\n"
        f"Active Users (Last 24h): {active_count}\n"
        f"Total Members: {chat_data[chat_id]['member_count']}\n"
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
    
    chat_id = chat.id
    user_id = user.id
    afk_msg = " ".join(context.args) or "AFK - Be right back!"
    if update.message.reply_to_message:
        afk_msg = update.message.reply_to_message.text
    
    afk_users[(chat_id, user_id)] = {"time": datetime.now(), "message": afk_msg}
    await update.message.reply_text(f"✨ {user.first_name} is now AFK! Reason: {afk_msg}")
