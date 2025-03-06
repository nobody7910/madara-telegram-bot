# handlers/group.py
import logging
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import Forbidden

logger = logging.getLogger(__name__)

# In-memory message tracking (use a DB for production)
message_counts = {}

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
        message_counts[chat_id][user_id] = {"daily": {}, "monthly": 0}
    if today not in message_counts[chat_id][user_id]["daily"]:
        message_counts[chat_id][user_id]["daily"][today] = 0
    message_counts[chat_id][user_id]["daily"][today] += 1
    message_counts[chat_id][user_id]["monthly"] += 1

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user if not message.reply_to_message else message.reply_to_message.from_user
    
    info_text = (
        f"🎯 User Spotlight: {user.first_name} 🎯\n"
        f"ID: `{user.id}`\n"
        f"Username: {f'@{user.username}' if user.username else 'None'}\n"
        f"Ready to rock this group! 🚀"
    )
    await message.reply_text(info_text, parse_mode="Markdown")

async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)
    
    today_count = sum(user["daily"].get(today, 0) for user in message_counts.get(chat_id, {}).values())
    yesterday_count = sum(user["daily"].get(yesterday, 0) for user in message_counts.get(chat_id, {}).values())
    monthly_count = sum(user["monthly"] for user in message_counts.get(chat_id, {}).values())
    
    stats = (
        f"📊 Group Stats for {chat.title} 📊\n"
        f"Today: {today_count} messages\n"
        f"Yesterday: {yesterday_count} messages\n"
        f"This Month: {monthly_count} messages\n"
        f"Keep the chatter going! 🔥"
    )
    await update.message.reply_text(stats)

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    user = message.from_user
    
    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command works only in groups!")
        return
    
    admins = await chat.get_administrators()
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can mute people, punk! 😛")
        return
    
    if not message.reply_to_message:
        await message.reply_text("Reply to someone to mute them, genius!")
        return
    
    target = message.reply_to_message.from_user
    if target.id in [admin.user.id for admin in admins]:
        await message.reply_text(
            f"Hey {user.first_name}, you stupid? You think I’m gonna mute an admin like {target.first_name}? "
            "Get outta here with that nonsense! 😂"
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
    if user.id not in [admin.user.id for admin in admins]:
        await message.reply_text("Only admins can summon the crew with /members! 😛")
        return
    
    members = await chat.get_members()
    member_list = [m.user for m in members if not m.user.is_bot]
    if not member_list:
        await message.reply_text("No members to tag? This group’s a ghost town! 👻")
        return
    
    await message.reply_text("Calling all members! Assemble! 🔔")
    for i in range(0, len(member_list), 8):
        batch = member_list[i:i+8]
        tags = " ".join(f"@{m.username}" if m.username else m.first_name for m in batch)
        try:
            await context.bot.send_message(chat_id=chat.id, text=tags)
            time.sleep(2)  # 2-second delay
        except Forbidden:
            await message.reply_text("Can’t tag some folks—privacy settings, ya know!")
            break

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command works only in groups!")
        return
    
    chat_id = str(chat.id)
    if chat_id not in message_counts or not message_counts[chat_id]:
        await update.message.reply_text("No chatter yet! Start talking to climb the ranks! 😛")
        return
    
    ranked = sorted(
        message_counts[chat_id].items(),
        key=lambda x: x[1]["monthly"],
        reverse=True
    )[:5]  # Top 5
    
    rank_text = f"🏆 Top Chatterboxes in {chat.title} 🏆\n"
    for i, (user_id, data) in enumerate(ranked, 1):
        user = await context.bot.get_chat_member(chat_id, int(user_id))
        rank_text += f"{i}. {user.user.first_name} - {data['monthly']} messages\n"
    
    await update.message.reply_text(rank_text)

# Placeholder for callback (if needed later)
async def handle_stat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass