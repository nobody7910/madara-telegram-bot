from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler  # Changed Filters to filters
from utils.helpers import get_user_photo, get_chat_photo
from datetime import datetime
import random
import time
from collections import defaultdict

# Rest of your code remains unchanged
# In-memory storage for message counts (replace with a database for persistence)
message_counts = defaultdict(int)
daily_counts = defaultdict(lambda: defaultdict(int))  # For today/tomorrow filtering

# Track all messages in the group to count them
async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type in ['group', 'supergroup']:
        user = update.effective_user
        if user and not user.is_bot:  # Ignore bots
            user_id = user.id
            current_time = time.time()
            current_day = time.strftime("%Y-%m-%d", time.localtime(current_time))
            current_month = time.strftime("%Y-%m", time.localtime(current_time))
            
            # Update total message count
            message_counts[user_id] += 1
            # Update daily count
            daily_counts[user_id][current_day] += 1

# ... (rest of your functions like start_group, stats, stat, etc., remain as-is)

# In-memory storage for message counts (replace with a database for persistence)
message_counts = defaultdict(int)
daily_counts = defaultdict(lambda: defaultdict(int))  # For today/tomorrow filtering

# Track all messages in the group to count them
async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type in ['group', 'supergroup']:
        user = update.effective_user
        if user and not user.is_bot:  # Ignore bots
            user_id = user.id
            current_time = time.time()
            current_day = time.strftime("%Y-%m-%d", time.localtime(current_time))
            current_month = time.strftime("%Y-%m", time.localtime(current_time))
            
            # Update total message count
            message_counts[user_id] += 1
            # Update daily count
            daily_counts[user_id][current_day] += 1

async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    args = context.args  # Check for start parameters

    # Check if started in PM with ?start=help
    if chat.type == 'private' and args and args[0] == "help":
        await send_help_summary(update, context, user)
        return

    # Original group start behavior
    bot_photo = await get_user_photo(bot, bot.id)
    intro_text = (
        f"🎉 *Greetings, {chat.title}!* 🎉\n"
        f"*Hey {user.first_name}!* 👋\n"
        f"[{user.username or user.full_name}]\n"
        "I’m @Madara7_chat_bot—your group stats manager bot by chilling friends! Add me to a group to unlock my powers.\n"
        "In PM, only /start, /help, and /info work.\n"
        "I’m your group’s new MVP.\n"
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
    chat = update.effective_chat
    member_count = await context.bot.get_chat_member_count(chat.id)
    creation_date = datetime.fromtimestamp(chat.id / (1 << 32)).strftime('%Y-%m-%d')  # Fixed: Renamed 'counts' to 'creation_date'
    photo = await get_chat_photo(context.bot, chat.id)
    stats_text = (
        f"[{user.username or user.full_name}]\n"
        f"*Group: {chat.title}*\n"
        f"Members: {member_count}\n"
        f"Created: {creation_date} (approx)"  # Fixed: Used creation_date
    )
    if photo:
        await update.message.reply_photo(photo=photo, caption=stats_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(stats_text, parse_mode="Markdown")

# New stat command with leaderboard
async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message

    # Check if the command is used in a group
    if chat.type not in ['group', 'supergroup']:
        await message.reply_text("This command can only be used in groups!")
        return

    # Get current time for filtering
    current_time = time.time()
    current_day = time.strftime("%Y-%m-%d", time.localtime(current_time))
    tomorrow_day = time.strftime("%Y-%m-%d", time.localtime(current_time + 86400))
    current_month = time.strftime("%Y-%m", time.localtime(current_time))

    # Default to total message counts
    leaderboard_data = message_counts

    # Sort users by message count and get top 10
    sorted_users = sorted(leaderboard_data.items(), key=lambda x: x[1], reverse=True)[:10]
    total_messages = sum(message_counts.values())

    # Build leaderboard text
    leaderboard_text = "📈 LEADERBOARD\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        try:
            user = await context.bot.get_chat(user_id)
            username = user.username if user.username else user.first_name
            profile_link = f"https://t.me/{username}" if user.username else f"tg://user?id={user_id}"
            name = user.first_name or "Unknown"
            leaderboard_text += (
                f"{i}. 👤 {name} ({profile_link}) • {count:,} ex.\n"
            )
        except:
            leaderboard_text += f"{i}. 👤 [User Left] • {count:,} ex.\n"

    leaderboard_text += f"\n✉️ Total messages: {total_messages:,}"

    # Inline buttons for filtering
    keyboard = [
        [
            InlineKeyboardButton("Today", callback_data="stat_today"),
            InlineKeyboardButton("Tomorrow", callback_data="stat_tomorrow"),
            InlineKeyboardButton("This Month", callback_data="stat_month"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the leaderboard
    await message.reply_text(leaderboard_text, reply_markup=reply_markup, parse_mode='Markdown')

# Handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat = query.message.chat
    if chat.type not in ['group', 'supergroup']:
        return

    current_time = time.time()
    current_day = time.strftime("%Y-%m-%d", time.localtime(current_time))
    tomorrow_day = time.strftime("%Y-%m-%d", time.localtime(current_time + 86400))
    current_month = time.strftime("%Y-%m", time.localtime(current_time))

    # Determine which filter to apply
    if query.data == "stat_today":
        leaderboard_data = {user_id: counts[current_day] for user_id, counts in daily_counts.items()}
        filter_label = "Today"
    elif query.data == "stat_tomorrow":
        leaderboard_data = {user_id: counts.get(tomorrow_day, 0) for user_id, counts in daily_counts.items()}
        filter_label = "Tomorrow"
    elif query.data == "stat_month":
        leaderboard_data = message_counts  # Simplified; extend with monthly tracking if needed
        filter_label = "This Month"
    else:
        return

    # Sort and get top 10
    sorted_users = sorted(leaderboard_data.items(), key=lambda x: x[1], reverse=True)[:10]
    total_messages = sum(leaderboard_data.values())

    # Build updated leaderboard text
    leaderboard_text = f"📈 LEADERBOARD ({filter_label})\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        try:
            user = await context.bot.get_chat(user_id)
            username = user.username if user.username else user.first_name
            profile_link = f"https://t.me/{username}" if user.username else f"tg://user?id={user_id}"
            name = user.first_name or "Unknown"
            leaderboard_text += (
                f"{i}. 👤 {name} ({profile_link}) • {count:,} ex.\n"
            )
        except:
            leaderboard_text += f"{i}. 👤 [User Left] • {count:,} ex.\n"

    leaderboard_text += f"\n✉️ Total messages: {total_messages:,}"

    # Reuse the same buttons
    keyboard = [
        [
            InlineKeyboardButton("Today", callback_data="stat_today"),
            InlineKeyboardButton("Tomorrow", callback_data="stat_tomorrow"),
            InlineKeyboardButton("This Month", callback_data="stat_month"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit the original message
    await query.edit_message_text(leaderboard_text, reply_markup=reply_markup, parse_mode='Markdown')

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"*Total members in {chat.title}:* {count}", parse_mode="Markdown")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.message.chat
    members = await context.bot.get_chat_administrators(chat.id)  # Use admins as proxy
    random.shuffle(members)  # Randomize for simulation
    top_text = f"*🏆 Top Admins in {chat.title} 🏆*\n\n"
    for i, member in enumerate(members[:5], 1):  # Top 5
        top_text += f"{i}. {member.user.full_name} (@{member.user.username or 'No username'}) - Activity: {random.randint(50, 200)} (simulated)\n"
    top_text += "\n*Note: Activity is simulated until tracking is added!*"
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
    print("Group /info command triggered")
    chat = update.effective_chat
    message = update.effective_message

    # Check if the command is used in a group
    if chat.type not in ['group', 'supergroup']:
        print(f"Chat type {chat.type} is not a group or supergroup")
        message.reply_text("This command can only be used in groups!")
        return
    print("Passed chat type check")

    # Determine the target user (replied-to user or the sender)
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        print(f"Target user (reply): {target_user.id}")
    else:
        target_user = update.effective_user
        print(f"Target user (self): {target_user.id}")

    # Get user details
    user_id = target_user.id
    first_name = target_user.first_name or "N/A"
    last_name = target_user.last_name or "N/A"
    username = f"@{target_user.username}" if target_user.username else "N/A"
    mention = f"[{first_name}](tg://user?id={user_id})"
    dc_id = target_user.dc_id or "N/A"  # Data center ID, might not always be available
    bio = "N/A"  # Telegram API doesn't provide bio directly via python-telegram-bot
    print("User details gathered")

    # Get profile photo count (requires Bot API interaction)
    try:
        photo_count = context.bot.get_user_profile_photos(user_id).total_count
        print(f"Photo count: {photo_count}")
    except Exception as e:
        photo_count = "N/A"
        print(f"Error getting photo count: {e}")

    # Get common chats (approximation, limited by privacy/API)
    common_groups = "N/A"  # This requires custom tracking or premium API access
    print("Common groups set to N/A")

    # Construct the info message
    info_text = (
        "【 User Information 】\n"
        f"➢ ID: `{user_id}`\n"
        f"➢ First Name: {first_name}\n"
        f"➢ Last Name: {last_name}\n"
        f"➢ Username: {username}\n"
        f"➢ Mention: {mention}\n"
        f"➢ DC ID: {dc_id}\n"
        f"➢ Bio: {bio}\n\n"
        "➢ Custom Bio: N/A\n"
        "➢ Custom Tag: N/A\n"
        f"➢ Profile Photos: {photo_count} Photos\n"
        "➢ Health: 100%\n"
        "    ▰▰▰▰▰▰▰▰▰▰\n\n"
        "➢ AFK Status: No\n"
        f"➢ Common Groups: {common_groups}\n"
        "➢ Globally Banned: No\n"
        "➢ Globally Muted: No"
    )
    print("Info text constructed")

    # Send the info as a reply
    try:
        message.reply_text(info_text, parse_mode='Markdown')
        print("Info message sent successfully")
    except Exception as e:
        print(f"Error sending info message: {e}")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat.type in ['group', 'supergroup']:
        intro_text = (
            "📚 *Need help with @Madara7_chat_bot?*\n"
            "I’m here to manage your group stats and more! Click below to see my full command list in DM."
        )
        keyboard = [
            [InlineKeyboardButton("Help", url=f"https://t.me/Madara7_chat_bot?start=help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(intro_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        user = update.effective_user
        await send_help_summary(update, context, user)