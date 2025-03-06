# handlers/pm.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    bot = context.bot

    keyboard = [[InlineKeyboardButton("📩 Get Full Help in PM", url=f"https://t.me/{bot.username}?start=help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if chat.type in ['group', 'supergroup']:
        await update.message.reply_text(
            "🤖 Click below for a detailed help guide in my private messages!",
            reply_markup=reply_markup
        )
        return

    full_help_message = (
        "🤖 Group Analytics Bot - Complete Command Guide 📊\n\n"
        "📌 Group Management:\n"
        "• /start - Bot introduction\n"
        "• /help - Command list\n"
        "👤 User Analysis:\n"
        "• /stat - User statistics\n"
        "• /info - Detailed user info\n"
        "👥 Group Insights:\n"
        "• /group_stats - Group stats\n"
        "• /top_members - Top members\n"
        "• /message_freq - Message frequency\n"
        "• /active - Active members\n"
        "• /leaderboard - Message leaderboard\n"
        "🔧 Admin:\n"
        "• /mute - Mute user\n"
        "• /top - Top admins\n"
    )
    await update.message.reply_text(full_help_message)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat

    if context.args and context.args[0] == 'help':
        await help_command(update, context)
        return

    bot_intro = (
        f"👋 Hello {user.first_name}! I'm a Group Analytics Bot\n\n"
        "Use /help to see all commands."
    ) if chat.type == 'private' else (
        f"👋 Hey {user.first_name}! I'm here to manage this group.\n\n"
        "Use /help to see what I can do!"
    )
    
    try:
        user_profile_photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if user_profile_photos.total_count > 0:
            await update.message.reply_photo(photo=user_profile_photos.photos[0][-1].file_id, caption=bot_intro)
        else:
            await update.message.reply_text(bot_intro)
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text(bot_intro)