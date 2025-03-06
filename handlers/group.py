# handlers/group.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes
from datetime import datetime
import random

logger = logging.getLogger(__name__)

message_logs = {}  # {chat_id: {user_id: [{'timestamp': datetime, 'count': int}, ...]}}

async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    
    try:
        chat_member = await context.bot.get_chat_member(chat.id, target_user.id)
        user_message_count = sum(log['count'] for log in message_logs.get(chat.id, {}).get(target_user.id, []))
        
        user_bio = "No bio available"
        stats_message = (
            f"👤 User Stats for {target_user.first_name}\n\n"
            f"📌 Name: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 User ID: {target_user.id}\n"
            f"👥 Status: {chat_member.status}\n"
            f"💬 Total Messages: {user_message_count}\n"
            f"📝 Bio: {user_bio}"
        )
        
        user_profile_photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
        if user_profile_photos.total_count > 0:
            await update.message.reply_photo(photo=user_profile_photos.photos[0][-1].file_id, caption=stats_message)
        else:
            await update.message.reply_text(stats_message)
    except Exception as e:
        logger.error(f"Error in stat command: {e}")
        await update.message.reply_text("Could not retrieve user stats.")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    
    try:
        chat_member = await context.bot.get_chat_member(chat.id, target_user.id) if chat.type in ['group', 'supergroup'] else None
        user_photos = await context.bot.get_user_profile_photos(target_user.id)
        photo_count = user_photos.total_count if user_photos else 0
        
        health_percentage = random.randint(80, 100)
        health_bar_length = 10
        filled_length = int(health_bar_length * health_percentage / 100)
        health_bar = '▰' * filled_length + '▱' * (health_bar_length - filled_length)
        
        info_message = (
            f"【 User Information 】\n\n"
            f"➢ ID: `{target_user.id}`\n"
            f"➢ First Name: {target_user.first_name}\n"
            f"➢ Last Name: {target_user.last_name or 'N/A'}\n"
            f"➢ Username: {f'@{target_user.username}' if target_user.username else 'N/A'}\n"
            f"➢ Mention: [{target_user.first_name}](tg://user?id={target_user.id})\n"
            f"➢ Profile Photos: {photo_count} Photos\n"
            f"➢ Health: {health_percentage}%\n"
            f"    {health_bar}\n"
        )
        
        user_profile_photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
        if user_profile_photos.total_count > 0:
            await update.message.reply_photo(photo=user_profile_photos.photos[0][-1].file_id, caption=info_message, parse_mode='Markdown')
        else:
            await update.message.reply_text(info_message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in info command: {e}")
        await update.message.reply_text("Could not retrieve user information.")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user to mute them.")
        return
    
    target_user = update.message.reply_to_message.from_user
    
    try:
        command_user_member = await context.bot.get_chat_member(chat.id, user.id)
        target_user_member = await context.bot.get_chat_member(chat.id, target_user.id)
        
        if target_user_member.status in ['administrator', 'creator']:
            await update.message.reply_text(random.choice([
                "🚫 Nice try! I can't mute an admin!",
                "😂 Oops! Admins are immune to mute magic!"
            ]))
            return
        
        if command_user_member.status in ['administrator', 'creator']:
            await context.bot.restrict_chat_member(
                chat.id, target_user.id, permissions=ChatPermissions(can_send_messages=False)
            )
            await update.message.reply_text(f"🤫 {target_user.first_name} has been muted!")
        else:
            await update.message.reply_text("Only admins can use this command.")
    except Exception as e:
        logger.error(f"Error in mute command: {e}")
        await update.message.reply_text("Could not complete the mute action.")

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        sorted_admins = sorted(
            admins,
            key=lambda a: sum(log['count'] for log in message_logs.get(chat.id, {}).get(a.user.id, [])),
            reverse=True
        )
        
        top_admins_message = "🏆 Top Administrators:\n\n"
        for idx, admin in enumerate(sorted_admins[:5], 1):
            message_count = sum(log['count'] for log in message_logs.get(chat.id, {}).get(admin.user.id, []))
            top_admins_message += (
                f"{idx}. {admin.user.first_name} {admin.user.last_name or ''}\n"
                f"   Role: {admin.status}\n"
                f"   Messages: {message_count}\n\n"
            )
        await update.message.reply_text(top_admins_message)
    except Exception as e:
        logger.error(f"Error in top command: {e}")
        await update.message.reply_text("Could not retrieve top administrators.")

async def active_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    
    try:
        total_members = await context.bot.get_chat_member_count(chat.id)
        group_message_counts = message_logs.get(chat.id, {})
        
        ACTIVE_THRESHOLD = 10
        active_members = [
            user_id for user_id, logs in group_message_counts.items()
            if sum(log['count'] for log in logs) >= ACTIVE_THRESHOLD
        ]
        
        active_message = (
            f"📊 Group Activity Report\n\n"
            f"👥 Total Members: {total_members}\n"
            f"🌟 Active Members: {len(active_members)}\n"
            f"📈 Activity Threshold: {ACTIVE_THRESHOLD} messages\n\n"
            "🔥 Top Active Members:\n"
        )
        
        sorted_active = sorted(
            active_members,
            key=lambda uid: sum(log['count'] for log in group_message_counts.get(uid, [])),
            reverse=True
        )
        
        for idx, user_id in enumerate(sorted_active[:10], 1):
            try:
                user = await context.bot.get_chat_member(chat.id, user_id)
                message_count = sum(log['count'] for log in group_message_counts.get(user_id, []))
                active_message += (
                    f"{idx}. {user.user.first_name} {user.user.last_name or ''}\n"
                    f"   💬 Messages: {message_count}\n"
                )
            except Exception:
                continue
        await update.message.reply_text(active_message)
    except Exception as e:
        logger.error(f"Error in active command: {e}")
        await update.message.reply_text("Could not retrieve group activity.")

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.effective_chat.type in ['group', 'supergroup']:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        current_time = datetime.now()
        
        if chat_id not in message_logs:
            message_logs[chat_id] = {}
        if user_id not in message_logs[chat_id]:
            message_logs[chat_id][user_id] = []
        
        message_logs[chat_id][user_id].append({'timestamp': current_time, 'count': 1})

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    bot = context.bot
    time_filter = context.args[0] if context.args else 'all'
    
    try:
        chat_members = await bot.get_chat_administrators(chat.id)
        now = datetime.now()
        leaderboard = []
        
        for user_id, message_log in message_logs.get(chat.id, {}).items():
            if time_filter == 'today':
                filtered_messages = [log for log in message_log if (now - log['timestamp']).days < 1]
            elif time_filter == 'yesterday':
                filtered_messages = [log for log in message_log if 1 <= (now - log['timestamp']).days < 2]
            elif time_filter == 'month':
                filtered_messages = [log for log in message_log if (now - log['timestamp']).days < 30]
            else:
                filtered_messages = message_log
            
            total_messages = len(filtered_messages)
            user_member = next((m for m in chat_members if m.user.id == user_id), None)
            
            if user_member and total_messages > 0:
                leaderboard.append({
                    'user_id': user_id,
                    'name': user_member.user.first_name,
                    'username': user_member.user.username,
                    'messages': total_messages
                })
        
        leaderboard.sort(key=lambda x: x['messages'], reverse=True)
        total_messages = sum(user['messages'] for user in leaderboard)
        leaderboard_message = "📈 LEADERBOARD\n\n"
        for idx, user in enumerate(leaderboard[:10], 1):
            username = f"@{user['username']}" if user['username'] else user['name']
            user_link = f"https://t.me/{user['username']}" if user['username'] else f"tg://user?id={user['user_id']}"
            leaderboard_message += (
                f"{idx}. {'👤' if idx % 2 == 0 else '👦🏻'} "
                f"[{user['name']}]({user_link}) • {user['messages']} msg\n"
            )
        
        leaderboard_message += f"\n✉️ Total messages: {total_messages}"
        keyboard = [
            [
                InlineKeyboardButton("Today", callback_data="stat_today"),
                InlineKeyboardButton("Yesterday", callback_data="stat_yesterday"),
                InlineKeyboardButton("This Month", callback_data="stat_month")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        chat_photo = await bot.get_chat(chat.id)
        if chat_photo.photo:
            await update.message.reply_photo(
                photo=chat_photo.photo.big_file_id,
                caption=leaderboard_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                leaderboard_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in leaderboard command: {e}")
        await update.message.reply_text("Could not retrieve group statistics.")

async def handle_stat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    time_filter = query.data.split('_')[1]
    context.args = [time_filter]
    await leaderboard_command(update, context)