import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
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
        [InlineKeyboardButton("𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦📜", callback_data="commands_start_0")]
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

# Updated commands list for the help menu and commands menu
COMMANDS_LIST = [
    "info", "photo", "stat", "members", "top", "mute", "unmute", "active", 
    "rank", "warn", "kick", "ban", "afk", "fun", "filter", "couple", "whisper", "fonts"
]

# Pagination settings
COMMANDS_PER_PAGE = 9  # Matches your example image (3 rows x 3 columns)

# Command summaries (shared between help_command and commands_menu)
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
    "help_fun": (
        "🎉 **Unleash the Fun Commands!** 🎉\n"
        "Tap below to see a wild list of anime-inspired actions! 🌟\n"
        "From hugs to bonks, I’ve got the vibes covered! 😎"
    ),
    "help_filter": (
        "🌀 /filter - Sets a custom response for a trigger word in groups!\n"
        "✋ /stop - Removes a filter (e.g., /stop hello)!\n"
        "📜 /filterlist - Lists all active filters in the group!"
    ),
    "help_couple": "💑 /couple - Picks a random couple from group admins!",
    "help_whisper": "💬 /whisper - Sends a secret message to a user in groups (inline)!",
    "help_fonts": "🖋️ /fonts - Styles your text with cool fonts!"
}

# Fun command summaries (2-3 lines each, derived from FUN_CAPTIONS but simplified)
FUN_SUMMARIES = {
    "waifu": (
        "🌸 **/waifu** 🌸\n"
        "Summons a dazzling waifu image!\n"
        "Perfect for anime fans! ✨"
    ),
    "neko": (
        "😺 **/neko** 😺\n"
        "Sends a cute neko pic!\n"
        "Cuddly cat vibes incoming! 💖"
    ),
    "shinobu": (
        "⚔️ **/shinobu** ⚔️\n"
        "Brings Shinobu’s epic grace!\n"
        "Elegance in every move! 🌟"
    ),
    "megumin": (
        "💥 **/megumin** 💥\n"
        "Unleashes Megumin’s explosive magic!\n"
        "Boom goes the fun! 🔥"
    ),
    "bully": (
        "😈 **/bully** 😈\n"
        "Teases with a playful bully action!\n"
        "Watch out for the taunts! 👊"
    ),
    "cuddle": (
        "🥰 **/cuddle** 🥰\n"
        "Wraps you in a warm cuddle!\n"
        "Feel the cozy love! 🤗"
    ),
    "cry": (
        "😢 **/cry** 😢\n"
        "Floods the chat with tears!\n"
        "Dramatic sobbing ahead! 💦"
    ),
    "hug": (
        "🤗 **/hug** 🤗\n"
        "Delivers a big, friendly hug!\n"
        "Spread the warmth! 💞"
    ),
    "awoo": (
        "🐺 **/awoo** 🐺\n"
        "Howls a wild awoo call!\n"
        "Unleash your inner wolf! 🌙"
    ),
    "kiss": (
        "💋 **/kiss** 💋\n"
        "Plants a sweet kiss on someone!\n"
        "Love is in the air! 😘"
    ),
    "lick": (
        "👅 **/lick** 👅\n"
        "Sneaks in a cheeky lick!\n"
        "Playful and quirky! 😏"
    ),
    "pat": (
        "✋ **/pat** ✋\n"
        "Gives a gentle head pat!\n"
        "Soothing and sweet! 🥳"
    ),
    "smug": (
        "😏 **/smug** 😏\n"
        "Flashes a smug, confident grin!\n"
        "Too cool for school! ✨"
    ),
    "bonk": (
        "🔨 **/bonk** 🔨\n"
        "Whacks with a mighty bonk!\n"
        "Time to behave! 💥"
    ),
    "yeet": (
        "🚀 **/yeet** 🚀\n"
        "Yeets someone into orbit!\n"
        "Outta here in style! 🌌"
    ),
    "blush": (
        "😳 **/blush** 😳\n"
        "Turns red with a shy blush!\n"
        "Too cute to handle! 💖"
    ),
    "smile": (
        "😊 **/smile** 😊\n"
        "Brightens up with a smile!\n"
        "Pure joy incoming! 🌞"
    ),
    "wave": (
        "👋 **/wave** 👋\n"
        "Sends a cheerful wave!\n"
        "Hey there, buddy! 🎉"
    ),
    "highfive": (
        "🖐️ **/highfive** 🖐️\n"
        "Slams a high-five!\n"
        "Teamwork makes the dream work! 🔥"
    ),
    "handhold": (
        "🤝 **/handhold** 🤝\n"
        "Holds hands sweetly!\n"
        "Aww, so wholesome! 💕"
    ),
    "nom": (
        "🍽️ **/nom** 🍽️\n"
        "Noms like a tasty snack!\n"
        "Chomp chomp! 😋"
    ),
    "bite": (
        "🦷 **/bite** 🦷\n"
        "Chomps with a playful bite!\n"
        "Ouch, but fun! 😈"
    ),
    "glomp": (
        "💖 **/glomp** 💖\n"
        "Tackles with a big glomp!\n"
        "Love attack incoming! 🏃"
    ),
    "slap": (
        "✋ **/slap** ✋\n"
        "Lands a legendary slap!\n"
        "Smackdown time! 💥"
    ),
    "kill": (
        "⚰️ **/kill** ⚰️\n"
        "Dramatically ends someone!\n"
        "Over-the-top fun! 💀"
    ),
    "kickk": (
        "👢 **/kickk** 👢\n"
        "Boots with a stylish kick!\n"
        "See ya later! 💨"
    ),
    "happy": (
        "🎉 **/happy** 🎉\n"
        "Spreads pure happiness!\n"
        "Joy overload! 😄"
    ),
    "wink": (
        "😉 **/wink** 😉\n"
        "Winks with sly charm!\n"
        "Smooth moves! ✨"
    ),
    "poke": (
        "👈 **/poke** 👈\n"
        "Pokes for some giggles!\n"
        "Hey, pay attention! 😆"
    ),
    "dance": (
        "💃 **/dance** 💃\n"
        "Grooves with wild dance moves!\n"
        "Party time! 🕺"
    ),
    "cringe": (
        "😬 **/cringe** 😬\n"
        "Cringes hard for laughs!\n"
        "Awkwardly hilarious! 😂"
    )
}

async def commands_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the commands menu with pagination and fun sub-menu."""
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
                button_text = "📊 sᴛᴀᴛ"
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
            elif cmd == "filter":
                button_text = "🌀 ғɪʟᴛᴇʀ"
            elif cmd == "couple":
                button_text = "💑 ᴄᴏᴜᴘʟᴇ"
            elif cmd == "whisper":
                button_text = "💬 ᴡʜɪsᴘᴇʀ"
            elif cmd == "fonts":
                button_text = "🖋️ ғᴏɴᴛs"

            row.append(InlineKeyboardButton(button_text, callback_data=f"cmd_{cmd}_{page}"))
            if (idx + 1) % 3 == 0 or idx == len(current_commands) - 1:
                keyboard.append(row)
                row = []

        # Add navigation buttons (backward, back, forward, close)
        total_pages = (len(COMMANDS_LIST) + COMMANDS_PER_PAGE - 1) // COMMANDS_PER_PAGE
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀", callback_data=f"commands_start_{page - 1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("◀", callback_data="noop"))
        nav_buttons.append(InlineKeyboardButton("BACK", callback_data="commands_back"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("▶", callback_data=f"commands_start_{page + 1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("▶", callback_data="noop"))
        nav_buttons.append(InlineKeyboardButton("🗑️", callback_data="commands_close"))

        keyboard.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)
        help_text = (
            "🫧 Mᴀᴅᴀʀᴀ Cʜᴀᴛ 🫧\n"
            f"⬇️ Lɪsᴛ Pᴀɢᴇ {page + 1}/{total_pages}\n"
            "☉ Hᴇʀᴇ, ʏᴏᴜ ᴡɪʟʟ ғɪɴᴅ ᴀ ʟɪsᴛ ᴏғ ᴀʟʟ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ : /"
            
        )

        if query.message.photo:
            await query.edit_message_caption(caption=help_text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=help_text, reply_markup=reply_markup, parse_mode="Markdown")
        await query.answer()

    elif data.startswith("cmd_"):
        parts = data.split("_")
        cmd = parts[1]
        page = int(parts[2])

        if cmd == "fun":
            # Pagination for fun commands
            fun_per_page = 9
            fun_commands = list(FUN_COMMANDS.keys())
            total_fun_pages = (len(fun_commands) + fun_per_page - 1) // fun_per_page
            fun_page = 0  # Default to first page

            start_idx = fun_page * fun_per_page
            end_idx = start_idx + fun_per_page
            current_fun_commands = fun_commands[start_idx:end_idx]

            fun_keyboard = []
            row = []
            for idx, fun_cmd in enumerate(current_fun_commands):
                row.append(InlineKeyboardButton(f"/{fun_cmd}", callback_data=f"fun_{fun_cmd}_{page}_{fun_page}"))
                if (idx + 1) % 3 == 0 or idx == len(current_fun_commands) - 1:
                    fun_keyboard.append(row)
                    row = []

            # Add navigation for fun commands
            nav_buttons = []
            if fun_page > 0:
                nav_buttons.append(InlineKeyboardButton("◀", callback_data=f"fun_page_{page}_{fun_page - 1}"))
            else:
                nav_buttons.append(InlineKeyboardButton("◀", callback_data="noop"))
            nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"commands_start_{page}"))
            if fun_page < total_fun_pages - 1:
                nav_buttons.append(InlineKeyboardButton("▶", callback_data=f"fun_page_{page}_{fun_page + 1}"))
            else:
                nav_buttons.append(InlineKeyboardButton("▶", callback_data="noop"))
            fun_keyboard.append(nav_buttons)

            reply_markup = InlineKeyboardMarkup(fun_keyboard)
            fun_text = (
                "🎉 **Fun Command List!** 🎉\n"
                f"Page {fun_page + 1}/{total_fun_pages}\n"
                "Tap a button to see what each does!\n"
            )
            if query.message.photo:
                await query.edit_message_caption(caption=fun_text, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.edit_message_text(text=fun_text, reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer()

        elif data.startswith("cmd_fun_"):
            fun_cmd = parts[2]
            summary = FUN_SUMMARIES.get(fun_cmd, f"/{fun_cmd} - Does something fun!")
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data=f"cmd_fun_{page}_0")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            if query.message.photo:
                await query.edit_message_caption(caption=summary, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.edit_message_text(text=summary, reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer()

    elif data.startswith("fun_page_"):
        parts = data.split("_")
        page = int(parts[2])
        fun_page = int(parts[3])

        fun_per_page = 9
        fun_commands = list(FUN_COMMANDS.keys())
        total_fun_pages = (len(fun_commands) + fun_per_page - 1) // fun_per_page

        start_idx = fun_page * fun_per_page
        end_idx = start_idx + fun_per_page
        current_fun_commands = fun_commands[start_idx:end_idx]

        fun_keyboard = []
        row = []
        for idx, fun_cmd in enumerate(current_fun_commands):
            row.append(InlineKeyboardButton(f"/{fun_cmd}", callback_data=f"fun_{fun_cmd}_{page}_{fun_page}"))
            if (idx + 1) % 3 == 0 or idx == len(current_fun_commands) - 1:
                fun_keyboard.append(row)
                row = []

        nav_buttons = []
        if fun_page > 0:
            nav_buttons.append(InlineKeyboardButton("◀", callback_data=f"fun_page_{page}_{fun_page - 1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("◀", callback_data="noop"))
        nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"commands_start_{page}"))
        if fun_page < total_fun_pages - 1:
            nav_buttons.append(InlineKeyboardButton("▶", callback_data=f"fun_page_{page}_{fun_page + 1}"))
        else:
            nav_buttons.append(InlineKeyboardButton("▶", callback_data="noop"))
        fun_keyboard.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(fun_keyboard)
        fun_text = (
            "🎉 **Fun Command List!** 🎉\n"
            f"Page {fun_page + 1}/{total_fun_pages}\n"
            "Tap a button to see what each does!\n"
        )
        if query.message.photo:
            await query.edit_message_caption(caption=fun_text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=fun_text, reply_markup=reply_markup, parse_mode="Markdown")
        await query.answer()

    elif data.startswith("fun_"):
        parts = data.split("_")
        fun_cmd = parts[1]
        page = int(parts[2])
        fun_page = int(parts[3])
        summary = FUN_SUMMARIES.get(fun_cmd, f"/{fun_cmd} - Does something fun!")
        back_button = [[InlineKeyboardButton("⬅️ Back", callback_data=f"fun_page_{page}_{fun_page}")]]
        reply_markup = InlineKeyboardMarkup(back_button)
        if query.message.photo:
            await query.edit_message_caption(caption=summary, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=summary, reply_markup=reply_markup, parse_mode="Markdown")
        await query.answer()

    elif data.startswith("cmd_"):
        parts = data.split("_")
        cmd = parts[1]
        page = int(parts[2])
        summary = SUMMARIES.get(f"help_{cmd}", f"No description available for /{cmd}.")
        back_button = [[InlineKeyboardButton("⬅️ Back", callback_data=f"commands_start_{page}")]]
        reply_markup = InlineKeyboardMarkup(back_button)
        if query.message.photo:
            await query.edit_message_caption(caption=summary, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=summary, reply_markup=reply_markup, parse_mode="Markdown")
        await query.answer()

    elif data == "commands_back":
        await start(update, context)
        await query.answer()

    elif data == "commands_close":
        if query.message.photo:
            await query.edit_message_caption(caption="Commands closed! Hit /start to reopen! 👋")
        else:
            await query.edit_message_text(text="Commands closed! Hit /start to reopen! 👋")
        await query.answer()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    query = update.callback_query
    
    if not query or query.data in ["help_back", "help_start"]:
        keyboard = [
            [InlineKeyboardButton("ℹ️ ɪɴғᴏ", callback_data="help_info"),
             InlineKeyboardButton("📸 ᴘʜᴏᴛᴏ", callback_data="help_photo"),
             InlineKeyboardButton("📊 sᴛᴀᴛ", callback_data="help_stat")],
            [InlineKeyboardButton("👥 ᴍᴇᴍʙᴇʀs", callback_data="help_members"),
             InlineKeyboardButton("🏆 ᴛᴏᴘ", callback_data="help_top"),
             InlineKeyboardButton("🔇 ᴍᴜᴛᴇ", callback_data="help_mute")],
            [InlineKeyboardButton("🔊 ᴜɴᴍᴜᴛᴇ", callback_data="help_unmute"),
             InlineKeyboardButton("🌟 ᴀᴄᴛɪᴠᴇ", callback_data="help_active"),
             InlineKeyboardButton("🥇 ʀᴀɴᴋ", callback_data="help_rank")],
            [InlineKeyboardButton("⚠️ ᴡᴀʀɴ", callback_data="help_warn"),
             InlineKeyboardButton("👢 ᴋɪᴄᴋ", callback_data="help_kick"),
             InlineKeyboardButton("🚫 ʙᴀɴ", callback_data="help_ban")],
            [InlineKeyboardButton("😴 ᴀғᴋ", callback_data="help_afk"),
             InlineKeyboardButton("🎉 ғᴜɴ", callback_data="help_fun_0"),
             InlineKeyboardButton("🌀 ғɪʟᴛᴇʀ", callback_data="help_filter")],
            [InlineKeyboardButton("💑 ᴄᴏᴜᴘʟᴇ", callback_data="help_couple"),
             InlineKeyboardButton("💬 ᴡʜɪsᴘᴇʀ", callback_data="help_whisper"),
             InlineKeyboardButton("🖋️ ғᴏɴᴛs", callback_data="help_fonts")],
            [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="help_close")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        help_text = (
            "нєу вυ∂∂у 🫣 нєяє му ¢σммαη∂ ℓιѕт\n"
            "тαρ ση вυттσѕ тσ кησω ωнαт тнιηgѕ ι ¢αη ∂σ 🗿😎\n\n"
            "Commands: /help, /info, /photo, /stat, /members, /top, /mute, /unmute, /active, /rank, /warn, /kick, /ban, /afk, /filter, /couple, /whisper, /fonts..."
        )
        if query:
            if query.message.photo:
                await query.edit_message_caption(caption=help_text, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.edit_message_text(text=help_text, reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer()
        else:
            await context.bot.send_message(chat_id=chat.id, text=help_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    else:
        data = query.data
        if data == "help_close":
            if query.message.photo:
                await query.edit_message_caption(caption="Help closed! Hit /help anytime to reopen! 👋")
            else:
                await query.edit_message_text(text="Help closed! Hit /help anytime to reopen! 👋")
            await query.answer()
            return
        
        if data.startswith("help_fun_"):
            fun_page = int(data.split("_")[-1])
            fun_per_page = 9
            fun_commands = list(FUN_COMMANDS.keys())
            total_fun_pages = (len(fun_commands) + fun_per_page - 1) // fun_per_page

            start_idx = fun_page * fun_per_page
            end_idx = start_idx + fun_per_page
            current_fun_commands = fun_commands[start_idx:end_idx]

            fun_keyboard = []
            row = []
            for idx, cmd in enumerate(current_fun_commands):
                row.append(InlineKeyboardButton(f"/{cmd}", callback_data=f"fun_{cmd}_{fun_page}"))
                if (idx + 1) % 3 == 0 or idx == len(current_fun_commands) - 1:
                    fun_keyboard.append(row)
                    row = []

            nav_buttons = []
            if fun_page > 0:
                nav_buttons.append(InlineKeyboardButton("◀", callback_data=f"help_fun_{fun_page - 1}"))
            else:
                nav_buttons.append(InlineKeyboardButton("◀", callback_data="noop"))
            nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data="help_back"))
            if fun_page < total_fun_pages - 1:
                nav_buttons.append(InlineKeyboardButton("▶", callback_data=f"help_fun_{fun_page + 1}"))
            else:
                nav_buttons.append(InlineKeyboardButton("▶", callback_data="noop"))
            nav_buttons.append(InlineKeyboardButton("❌ Close", callback_data="help_close"))
            fun_keyboard.append(nav_buttons)

            reply_markup = InlineKeyboardMarkup(fun_keyboard)
            fun_text = (
                "🎉 **Fun Command List!** 🎉\n"
                f"Page {fun_page + 1}/{total_fun_pages}\n"
                "Tap a button to see what each does!\n"
            )
            if query.message.photo:
                await query.edit_message_caption(caption=fun_text, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.edit_message_text(text=fun_text, reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer()

        elif data.startswith("fun_"):
            parts = data.split("_")
            cmd = parts[1]
            fun_page = int(parts[2])
            summary = FUN_SUMMARIES.get(cmd, f"/{cmd} - Does something fun!")
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data=f"help_fun_{fun_page}")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            if query.message.photo:
                await query.edit_message_caption(caption=summary, reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.edit_message_text(text=summary, reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer()

        elif data in SUMMARIES:
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_back"),
                            InlineKeyboardButton("❌ Close", callback_data="help_close")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            if query.message.photo:
                await query.edit_message_caption(caption=SUMMARIES[data], reply_markup=reply_markup, parse_mode="Markdown")
            else:
                await query.edit_message_text(text=SUMMARIES[data], reply_markup=reply_markup, parse_mode="Markdown")
            await query.answer()
