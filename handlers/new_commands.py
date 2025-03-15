# handlers/new_commands.py
import logging
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, InlineQueryHandler, MessageHandler, filters, CallbackQueryHandler, CommandHandler
import aiohttp
from pyfiglet import Figlet
from utils.db import get_db
from uuid import uuid4

logger = logging.getLogger(__name__)

# Async helper function to get the filters collection
async def get_filters_collection():
    db = await get_db()
    return db.get_collection("filters")

# --- Couple Command ---
async def couple_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in groups! 👥")
        return

    try:
        # Fetch administrators
        admins = await context.bot.get_chat_administrators(chat.id)
        members = [admin.user for admin in admins if not admin.user.is_bot]
        if len(members) < 2:
            await context.bot.send_message(
                chat_id=chat.id,
                text="Not enough non-bot members in the group to form a couple! 😅"
            )
            return

        user1, user2 = random.sample(members, 2)
        user1_link = f"tg://user?id={user1.id}"
        user2_link = f"tg://user?id={user2.id}"

        # Updated caption with first names and init links
        caption = (
            "🙈🎀𝗖❀𝗨𝗣𝗟𝗘 ❀𝗙 𝗧𝗛𝗘 𝗗𝗔𝗬😘🎀\n"
            f"♡\n"
            f"°\n"
            f"°❀💗\n"
            f"[{user1.first_name}]({user1_link}) + [{user2.first_name}]({user2_link}) = 💘\n"
            f"Mᴀʏ Yᴏᴜʀ ʟᴏᴠᴇ ʙʟᴏᴏᴍ🌸🌸\n"
            f"°ᴄ❀ᴜᴘʟᴇ ❣️\n"
            f"♡"
        )
        # Fetch image from waifu.pics
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.waifu.pics/sfw/waifu") as response:
                if response.status != 200:
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text="Couldn’t fetch a couple image. Try again later! 😓"
                    )
                    return
                data = await response.json()
                image_url = data["url"]

        await context.bot.send_photo(
            chat_id=chat.id,
            photo=image_url,
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in couple command: {e}")
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text="An error occurred while finding a couple. Try again later! 😓"
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")

# --- Whisper Command ---
async def whisper_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if not query:
        # Show the "Whisper" option when the user types @botusername
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Whisper 💬",
                description="Send a secret message to a user",
                input_message_content=InputTextMessageContent(
                    "Click to send a whisper message 💬\nFormat: @botusername <message> @username"
                )
            )
        ]
        await update.inline_query.answer(results)
        return

    bot = context.bot
    bot_username = bot.username.lower()
    pattern = rf"^{re.escape(bot_username)}\s+(.+?)\s+@(\w+)$"
    match = re.match(pattern, query.lower(), re.IGNORECASE)

    if not match:
        return

    message = match.group(1)
    username = match.group(2)

    try:
        chat = update.effective_chat
        if chat.type not in ["group", "supergroup"]:
            return

        # Fetch all chat members to find the target
        members = [m.user async for m in context.bot.get_chat_members(chat.id) if not m.user.is_bot]
        target_user = next((m for m in members if m.username and m.username.lower() == username.lower()), None)

        if not target_user:
            await update.inline_query.answer([])
            return

        # Store the whisper message in context.bot_data temporarily
        whisper_id = str(uuid4())
        context.bot_data[whisper_id] = {
            "sender": update.effective_user.first_name,
            "message": message,
            "target_user_id": target_user.id
        }

        # Create a button for the target user to view the whisper
        keyboard = [[InlineKeyboardButton("Open Whisper 🔒", callback_data=f"whisper_{whisper_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=target_user.id,
            text=f"💬 You have a whisper from {update.effective_user.first_name}!",
            reply_markup=reply_markup
        )
        await update.inline_query.answer([])
    except Exception as e:
        logger.error(f"Error in whisper command: {e}")
        await update.inline_query.answer([])

async def whisper_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user = query.from_user

    if not data.startswith("whisper_"):
        return

    whisper_id = data.split("_")[1]
    whisper_data = context.bot_data.get(whisper_id)

    if not whisper_data:
        await query.edit_message_text("This whisper has expired or does not exist.")
        await query.answer()
        return

    # Check if the user is the target user
    if user.id != whisper_data["target_user_id"]:
        await query.answer("This whisper is not for you! 🔒", show_alert=True)
        return

    # Reveal the message to the target user
    await query.edit_message_text(
        f"💬 *Whisper from {whisper_data['sender']}:* {whisper_data['message']}",
        parse_mode="Markdown"
    )
    await query.answer()

    # Clean up the stored whisper
    del context.bot_data[whisper_id]

# --- Fonts Command ---
async def fonts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message

    if not context.args:
        await message.reply_text("Please provide a message to style! E.g., /fonts Hello")
        return
    text = " ".join(context.args)

    # Updated FONTS dictionary with correct pyfiglet font names
    FONTS = {
        "Standard": "standard",
        "Big": "big",
        "Block": "block",
        "Bubble": "bubble",
        "Digital": "digital",
        "Lean": "lean",
        "Mini": "mini",
        "Script": "script",
        "Slant": "slant",
        "Small": "small",
        "3D": "3-d",
        "3x5": "3x5",
        "5LineOblique": "5lineoblique",
        "Alpha": "alphabet",
        "Banner": "banner3",
        "Doom": "doom",
        "Ghost": "ghost",
        "Gothic": "gothic",
        "Graceful": "graceful",
        "Isometric1": "isometric1",
        "Ogre": "ogre",
        "Rectangles": "rectangles",
        "Roman": "roman",
        "Shadow": "shadow",
        "Speed": "speed",
        "Stampatello": "stampatello",
        "Univers": "univers"
    }

    # Replicate the layout with updated font names
    keyboard = [
        [
            InlineKeyboardButton("Standard", callback_data=f"font_Standard_{text}"),
            InlineKeyboardButton("Big", callback_data=f"font_Big_{text}"),
            InlineKeyboardButton("Block", callback_data=f"font_Block_{text}")
        ],
        [
            InlineKeyboardButton("Bubble", callback_data=f"font_Bubble_{text}"),
            InlineKeyboardButton("Digital", callback_data=f"font_Digital_{text}"),
            InlineKeyboardButton("Lean", callback_data=f"font_Lean_{text}")
        ],
        [
            InlineKeyboardButton("Mini", callback_data=f"font_Mini_{text}"),
            InlineKeyboardButton("Script", callback_data=f"font_Script_{text}"),
            InlineKeyboardButton("Slant", callback_data=f"font_Slant_{text}")
        ],
        [
            InlineKeyboardButton("Small", callback_data=f"font_Small_{text}"),
            InlineKeyboardButton("3D", callback_data=f"font_3D_{text}"),
            InlineKeyboardButton("3x5", callback_data=f"font_3x5_{text}")
        ],
        [
            InlineKeyboardButton("5LineOblique", callback_data=f"font_5LineOblique_{text}"),
            InlineKeyboardButton("Alpha", callback_data=f"font_Alpha_{text}"),
            InlineKeyboardButton("Banner", callback_data=f"font_Banner_{text}")
        ],
        [
            InlineKeyboardButton("Doom", callback_data=f"font_Doom_{text}"),
            InlineKeyboardButton("Ghost", callback_data=f"font_Ghost_{text}"),
            InlineKeyboardButton("Gothic", callback_data=f"font_Gothic_{text}")
        ],
        [
            InlineKeyboardButton("Graceful", callback_data=f"font_Graceful_{text}"),
            InlineKeyboardButton("Isometric1", callback_data=f"font_Isometric1_{text}"),
            InlineKeyboardButton("Ogre", callback_data=f"font_Ogre_{text}")
        ],
        [
            InlineKeyboardButton("Rectangles", callback_data=f"font_Rectangles_{text}"),
            InlineKeyboardButton("Roman", callback_data=f"font_Roman_{text}"),
            InlineKeyboardButton("Shadow", callback_data=f"font_Shadow_{text}")
        ],
        [
            InlineKeyboardButton("Speed", callback_data=f"font_Speed_{text}"),
            InlineKeyboardButton("Stampatello", callback_data=f"font_Stampatello_{text}"),
            InlineKeyboardButton("Univers", callback_data=f"font_Univers_{text}")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="font_close")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        f"🖋️ Select a font to style your text: *{text}*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data == "font_close":
        await query.message.delete()
        await query.answer()
        return

    parts = data.split("_", 2)
    font_name = parts[1]
    text = parts[2]

    # Updated FONTS dictionary with correct pyfiglet font names
    FONTS = {
        "Standard": "standard",
        "Big": "big",
        "Block": "block",
        "Bubble": "bubble",
        "Digital": "digital",
        "Lean": "lean",
        "Mini": "mini",
        "Script": "script",
        "Slant": "slant",
        "Small": "small",
        "3D": "3-d",
        "3x5": "3x5",
        "5LineOblique": "5lineoblique",
        "Alpha": "alphabet",
        "Banner": "banner3",
        "Doom": "doom",
        "Ghost": "ghost",
        "Gothic": "gothic",
        "Graceful": "graceful",
        "Isometric1": "isometric1",
        "Ogre": "ogre",
        "Rectangles": "rectangles",
        "Roman": "roman",
        "Shadow": "shadow",
        "Speed": "speed",
        "Stampatello": "stampatello",
        "Univers": "univers"
    }

    font_key = FONTS.get(font_name, "standard")
    fig = Figlet(font=font_key)
    styled_text = fig.renderText(text)

    # Truncate styled_text to fit Telegram's message length limit (4096 characters)
    max_length = 4000  # Leave some buffer for the rest of the message
    if len(styled_text) > max_length:
        styled_text = styled_text[:max_length] + "\n...\n[Text truncated due to length]"

    # Add Back button
    keyboard = [
        [InlineKeyboardButton("⬅️ Back", callback_data=f"font_back_{text}")],
        [InlineKeyboardButton("❌ Close", callback_data="font_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(
            f"🖋️ *Styled Text ({font_name}):*\n```\n{styled_text}\n```",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error editing message in font_callback: {e}")
        await query.edit_message_text(
            f"🖋️ *Styled Text ({font_name}):*\nSorry, the styled text is too long to display. Try a shorter message!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    await query.answer()

# Handle Back button
async def font_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    if data.startswith("font_back_"):
        text = data.split("_", 2)[2]
        await fonts_command(update, context)  # Return to font selection
        await query.answer()

# --- Filter Command ---
async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message

    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command can only be used in groups! 👥")
        return

    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to set it as the filter response!")
        return

    if not context.args:
        await message.reply_text("Please provide a trigger word! E.g., /filter yoo")
        return

    trigger = context.args[0].lower()
    reply_message = message.reply_to_message

    # Handle different types of reply messages
    if reply_message.text:
        response = reply_message.text
    elif reply_message.caption:
        response = reply_message.caption
    elif reply_message.sticker:
        response = f"Sticker: {reply_message.sticker.file_id}"  # Use file_id for sticker
    elif reply_message.animation:
        response = f"GIF: {reply_message.animation.file_id}"  # Use file_id for GIF
    else:
        response = "Media message"

    filters_collection = await get_filters_collection()
    await filters_collection.update_one(
        {"chat_id": chat.id, "trigger": trigger},
        {"$set": {"response": response}},
        upsert=True
    )

    await message.reply_text(f"Filter set! Whenever someone says '{trigger}', I’ll respond with the replied message.")

# --- Stop Command for Filters ---
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message

    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command can only be used in groups! 👥")
        return

    if not context.args:
        return  # Silently ignore if no trigger is provided

    trigger = context.args[0].lower()
    filters_collection = await get_filters_collection()
    result = await filters_collection.delete_one({"chat_id": chat.id, "trigger": trigger})

    if result.deleted_count > 0:
        await message.reply_text(f"Filter for '{trigger}' has been removed.")
    else:
        await message.reply_text(f"No filter found for '{trigger}'.")

# --- Filter List Command ---
async def filterlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message

    if chat.type not in ["group", "supergroup"]:
        await message.reply_text("This command can only be used in groups! 👥")
        return

    filters_collection = await get_filters_collection()
    filters = await filters_collection.find({"chat_id": chat.id}).to_list(length=None)

    if not filters:
        await message.reply_text("No filters are set in this group.")
        return

    filter_list = "📌 Active Filters:\n\n"
    for i, filter_doc in enumerate(filters, 1):
        filter_list += f"{i}. Trigger: `{filter_doc['trigger']}`\n   Response: {filter_doc['response']}\n\n"

    await message.reply_text(filter_list, parse_mode="Markdown")

# --- Handle Filters ---
async def handle_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.message
    if chat is None or message is None:
        return

    if chat.type not in ["group", "supergroup"]:
        return

    # Extract content from the message
    content = ""
    if message.text:
        content = message.text.lower()
    elif message.caption:
        content = message.caption.lower()
    elif message.sticker and message.sticker.emoji:
        content = message.sticker.emoji.lower()
    elif message.animation:
        content = "gif"

    if not content:
        return  # Silently ignore messages with no relevant content

    # Fetch filters asynchronously using motor
    filters_collection = await get_filters_collection()
    filters = await filters_collection.find({"chat_id": chat.id}).to_list(length=None)
    for filter_doc in filters:
        trigger = filter_doc["trigger"]
        if trigger in content:
            response = filter_doc["response"]
            if "Sticker:" in response:
                await message.reply_sticker(response.split("Sticker: ")[1])
            elif "GIF:" in response:
                await message.reply_animation(response.split("GIF: ")[1])
            else:
                await message.reply_text(response)
