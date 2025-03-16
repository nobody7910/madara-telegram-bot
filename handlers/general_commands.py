# handlers/general_commands.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.group import chat_data, message_counts
from handlers.fun import FUN_COMMANDS  # Assuming FUN_COMMANDS is imported from fun.py

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    
    # Get bot's profile photo instead of user's
    bot_photos = await context.bot.get_user_profile_photos(context.bot.id, limit=1)
    user_link = f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"
    intro = (
        f"ɪᴀᴍ❂ Mᴀᴅᴀʀᴀ⚡️Cʜᴀᴛ🌀 ❂\n"
        f"× ʜᴇʟʟᴏ {user.first_name} ( [{user.first_name}]({user_link}) )\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f" Rᴇᴀᴅʏ ᴛᴏ ʀᴏʟʟ ᴜᴘ ᴡɪᴛʜ ᴍᴇ 🎉\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f"Hɪᴛ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ ᴏʀ ɢᴇᴛ ʜᴇʟᴘ! 🚀\n"
        f"Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ sǫᴜᴀᴅ ᴀɴᴅ ʟᴇᴛ’s ᴍᴀᴋᴇ ɪᴛ ʟᴇɢᴇɴᴅᴀʀʏ! 🌟\n"
        f"Qᴜᴇsᴛɪᴏɴs? Sᴜᴘᴘᴏʀᴛ’s ɢᴏᴛ ʏᴏᴜʀ ʙᴀᴄᴋ—ᴛᴀᴘ ʙᴇʟᴏᴡ! ☘️\n"
        f" ────────────── \n"
        f"𝐌ᴀᴅᴀʀᴀ 𝐔ᴄʜɪʜᴀ!! \n"
        f"Wᴀᴋᴇ ᴜᴘ ᴛᴏ ʀᴇᴀʟɪᴛʏ! ɴᴏᴛʜɪɴɢ ᴇᴠᴇʀ ɢᴏᴇs ᴀs ᴘʟᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ᴀᴄᴄᴜʀsᴇᴅ ᴡᴏʀʟᴅ.Tʜᴇ ʟᴏɴɢᴇʀ ʏᴏᴜ ʟɪᴠᴇ, ᴛʜᴇ ᴍᴏʀᴇ ʏᴏᴜ ʀᴇᴀʟɪᴢᴇ ᴛʜᴀᴛ ᴛʜᴇ ᴏɴʟʏ ᴛʜɪɴɢs ᴛʜᴀᴛ ᴛʀᴜʟʏ ᴇxɪsᴛ ɪɴ ᴛʜɪs ʀᴇᴀʟɪᴛʏ ᴀʀᴇ ᴍᴇʀᴇʟʏ ᴘᴀɪɴ, sᴜғғᴇʀɪɴɢ ᴀɴᴅ ғᴜᴛɪʟɪᴛʏ.!!"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗚𝗥𝗢𝗨𝗣", url="https://t.me/Madara7_chat_bot?startgroup=true")],
        [InlineKeyboardButton("ℹ️ 𝗜𝗡𝗙𝗢", url="https://t.me/Sung_jin_woo_79"),
         InlineKeyboardButton("📞 𝗦𝗨𝗣𝗣𝗢𝗥𝗧", url="https://t.me/+rh41IlhjtHVjZWY1")],
        [InlineKeyboardButton("𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦📜", callback_data="commands_start_0")]  # Moved to a new row
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if bot_photos.photos:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=bot_photos.photos[0][-1].file_id,
            caption=intro,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(
            chat_id=chat.id,
            text=intro,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# Existing commands list for the help menu (to reuse in commands menu)
COMMANDS_LIST = [
    "info", "photo", "stat", "members", "top", "mute", "unmute", "active", 
    "rank", "warn", "kick", "ban", "afk", "fun"
]

# Pagination settings
COMMANDS_PER_PAGE = 9  # Matches your example image (3 rows x 3 columns)

# Command summaries (moved here to be shared between help_command and commands_menu)
SUMMARIES = {
    "help_info": "ℹ️ /info - Shows user PFP + dope details!",
    "help_photo": "📸 /photo - Grabs recent PFPs!",
    "help_stat": "📊 /stat - Leaderboard with top chatters!",
    "help_members": "👥 /members - Tags all members (admin only)!",
    "help_top": "🏆 /top - Top 3 chatterboxes!",
    "help_mute": "🔇 /mute - Mutes a user (admin only) via reply or /mute @username!",
    "help_unmute": "🔊 /unmute - Unmutes a user (admin only) via reply or /unmute @username!",
    "help_active": "🌟 /active - Counts active users!",
    "help_rank": "🥇 /rank - Top 5 message senders!",
    "help_warn": "⚠️ /warn - Warns a user (admin only) via reply or /warn @username!",
    "help_kick": "👢 /kick - Kicks a user (admin only) via reply or /kick @username!",
    "help_ban": (
        "🚫 **BAN HAMMER ALERT!** 🚫\n"
        "🔒 /ban - Ban a user (admin only) via reply or /ban @username!\n"
        "🎉 Example: Banished [{user}](link) from *group*! 👋\n"
        "🌟 Keeps the group safe and epic! 🔥"
    ),
    "help_afk": "😴 /afk - Mark yourself AFK with a custom message!",
    "help_fun": "🎉 Fun Commands:\nRandom anime pics from waifu.pics!"
}

async def commands_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the commands menu with pagination, similar to /help."""
    query = update.callback_query
    data = query.data

    if data.startswith("commands_start_"):
        page = int(data.split("_")[-1])  # Extract the page number from callback_data
        
        # Calculate the start and end indices for the current page
        start_idx = page * COMMANDS_PER_PAGE
        end_idx = start_idx + COMMANDS_PER_PAGE
        current_commands = COMMANDS_LIST[start_idx:end_idx]

        # Prepare the keyboard layout (3x3 grid as in the example image)
        keyboard = []
        row = []
        for idx, cmd in enumerate(current_commands):
            button_text = cmd.upper()
            if cmd == "info":
                button_text = "ℹ️ ɪɴғᴏ"
            elif cmd == "photo":
                button_text = "📸 ᴘʜᴏᴛᴏ"
            elif cmd == "stat":
                button_text = "📊 sᴛᴀᴛ "
            elif cmd == "members":
                button_text = "👥 ᴍᴇᴍʙᴇʀs"
            elif cmd == "top":
                button_text = "🏆 ᴛᴏᴘ"
            elif cmd == "mute":
                button_text = "🔇 ᴍᴜᴛᴇ"
            elif cmd == "unmute":
                button_text = "🔊 ᴜɴᴍᴜᴛᴇ"
            elif cmd == "active":
                button_text = "🌟 ᴀᴄᴛɪᴠᴇ"
            elif cmd == "rank":
                button_text = "🥇 ʀᴀɴᴋ"
            elif cmd == "warn":
                button_text = "⚠️ ᴡᴀʀɴ"
            elif cmd == "kick":
                button_text = "👢 ᴋɪᴄᴋ"
            elif cmd == "ban":
                button_text = "🚫 ʙᴀɴ"
            elif cmd == "afk":
                button_text = "😴 ᴀғᴋ"
            elif cmd == "fun":
                button_text = "🎉 ғᴜɴ"

            # Include the page number in the callback data so we can return to the same page
            row.append(InlineKeyboardButton(button_text, callback_data=f"cmd_{cmd}_{page}"))
            if (idx + 1) % 3 == 0 or idx == len(current_commands) - 1:
                keyboard.append(row)
                row = []

        # Add navigation buttons (backward, back, forward, close)
        total_pages = (len(COMMANDS_LIST) + COMMANDS_PER_PAGE - 1) // COMMANDS_PER_PAGE
        nav_buttons = []
        
        # Backward button
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀", callback_data=f"commands_start_{page - 1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("◀", callback_data="noop"))  # Disabled button

        # Back button (returns to the start menu)
        nav_buttons.append(InlineKeyboardButton("BACK", callback_data="commands_back"))

        # Forward button
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("▶", callback_data=f"commands_start_{page + 1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("▶", callback_data="noop"))  # Disabled button

        # Close button (bin)
        nav_buttons.append(InlineKeyboardButton("🗑️", callback_data="commands_close"))

        keyboard.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)
        help_text = (
            "🫧 Mᴀᴅᴀʀᴀ Cʜᴀᴛ 🫧\n"
            f"⬇️ Lɪsᴛ Pᴀɢᴇ {page + 1}/{total_pages}\n"
            "☉ Hᴇʀᴇ, ʏᴏᴜ ᴡɪʟʟ ғɪɴᴅ ᴀ ʟɪsᴛ ᴏғ ᴀʟʟ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.\n"
            "ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ : /"
        )

        # Check if the original message is a photo and edit caption if true, otherwise edit text
        if query.message.photo:
            await query.edit_message_caption(caption=help_text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=help_text, reply_markup=reply_markup, parse_mode="Markdown")
        await query.answer()

    elif data.startswith("cmd_"):
        # Handle command summary display
        parts = data.split("_")
        cmd = parts[1]  # e.g., "info", "ban", etc.
        page = int(parts[2])  # The page to return to

        summary = SUMMARIES.get(f"help_{cmd}", f"No description available for /{cmd}.")
        
        back_button = [[InlineKeyboardButton("⬅️ Back", callback_data=f"commands_start_{page}")]]
        reply_markup = InlineKeyboardMarkup(back_button)

        if query.message.photo:
            await query.edit_message_caption(caption=summary, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=summary, reply_markup=reply_markup, parse_mode="Markdown")
        await query.answer()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    query = update.callback_query
    
    if not query or query.data in ["help_back", "help_start"]:
        keyboard = [
            [InlineKeyboardButton("ℹ️ ɪɴғᴏ", callback_data="help_info"),
             InlineKeyboardButton("📸 ᴘʜᴏᴛᴏ", callback_data="help_photo")],
            [InlineKeyboardButton("📊 sᴛᴀᴛ", callback_data="help_stat"),
             InlineKeyboardButton("👥 ᴍᴇᴍʙᴇʀs", callback_data="help_members")],
            [InlineKeyboardButton("🏆 ᴛᴏᴘ", callback_data="help_top"),
             InlineKeyboardButton("🔇 ᴍᴜᴛᴇ", callback_data="help_mute")],
            [InlineKeyboardButton("🔊 ᴜɴᴍᴜᴛᴇ", callback_data="help_unmute"),
             InlineKeyboardButton("🌟 ᴀᴄᴛɪᴠᴇ", callback_data="help_active")],
            [InlineKeyboardButton("🥇 ʀᴀɴᴋ", callback_data="help_rank"),
             InlineKeyboardButton("⚠️ ᴡᴀʀɴ", callback_data="help_warn")],
            [InlineKeyboardButton("👢 ᴋɪᴄᴋ", callback_data="help_kick"),
             InlineKeyboardButton("🚫 ʙᴀɴ", callback_data="help_ban")],  # Added Ban
            [InlineKeyboardButton("😴 ᴀғᴋ", callback_data="help_afk"),
             InlineKeyboardButton("🎉 ғᴜɴ", callback_data="help_fun")],
            [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="help_close")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        help_text = (
            "нєу вυ∂∂у 🫣 нєяє му ¢σммαη∂ ℓιѕт\n"
            "тαρ ση вυттσѕ тσ кησω ωнαт тнιηgѕ ι ¢αη ∂σ 🗿😎\n\n"
            "Commands: /help, /info, /photo, /stat, /members, /top, /mute, /unmute, /active, /rank, /warn, /kick, /ban, /afk, /waifus..."
        )
        if query:
            if query.message.photo:
                await query.edit_message_caption(caption=help_text, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.edit_message_text(text=help_text, reply_markup=reply_markup)
            await query.answer()
        else:
            await context.bot.send_message(chat_id=chat.id, text=help_text, reply_markup=reply_markup)
    else:
        data = query.data
        if data == "help_close":
            await query.edit_message_text("Help closed! Hit /help anytime to reopen! 👋")
            await query.answer()
            return
        
        if data in SUMMARIES:
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_back"),
                            InlineKeyboardButton("❌ Close", callback_data="help_close")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(SUMMARIES[data], reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer()
        elif data == "help_fun":
            fun_keyboard = [[InlineKeyboardButton(f"/{cmd}", callback_data=f"fun_{cmd}")] for cmd in FUN_COMMANDS.keys()]
            fun_keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="help_back"),
                                 InlineKeyboardButton("❌ Close", callback_data="help_close")])
            reply_markup = InlineKeyboardMarkup(fun_keyboard)
            await query.edit_message_text(SUMMARIES["help_fun"], reply_markup=reply_markup)
            await query.answer()
        elif data.startswith("fun_"):
            cmd = data.split("_")[1]
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_fun"),
                            InlineKeyboardButton("❌ Close", callback_data="help_close")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(f"/{cmd} - Fetches a random {cmd} image!", reply_markup=reply_markup)
            await query.answer()
