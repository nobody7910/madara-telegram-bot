# handlers/general_commands.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.group import chat_data, message_counts  # Import these from group.py
from handlers.fun import FUN_COMMANDS  # Import FUN_COMMANDS from fun.py

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    
    photos = await context.bot.get_user_profile_photos(user.id, limit=1)
    intro = (
        f"🎉 Yo yo, {user.first_name}! Welcome to the party! 🎉\n"
        f"I’m your slick bot—hit /help for the rundown!\n"
    )
    
    keyboard = [[InlineKeyboardButton("Add me to a group", callback_data="add_to_group")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if photos.photos:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=photos.photos[0][-1].file_id,
            caption=intro,
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat.id,
            text=intro,
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    query = update.callback_query
    
    if not query or query.data == "help_back":
        keyboard = [
            [InlineKeyboardButton("ℹ️ Info", callback_data="help_info"),
             InlineKeyboardButton("📸 Photo", callback_data="help_photo")],
            [InlineKeyboardButton("📊 Stat", callback_data="help_stat"),
             InlineKeyboardButton("👥 Members", callback_data="help_members")],
            [InlineKeyboardButton("🏆 Top", callback_data="help_top"),
             InlineKeyboardButton("🔇 Mute", callback_data="help_mute")],
            [InlineKeyboardButton("🔊 Unmute", callback_data="help_unmute"),
             InlineKeyboardButton("🌟 Active", callback_data="help_active")],
            [InlineKeyboardButton("🥇 Rank", callback_data="help_rank"),
             InlineKeyboardButton("⚠️ Warn", callback_data="help_warn")],
            [InlineKeyboardButton("👢 Kick", callback_data="help_kick"),
             InlineKeyboardButton("😴 AFK", callback_data="help_afk")],
            [InlineKeyboardButton("🎉 Fun", callback_data="help_fun")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        help_text = (
            "Yo! I’m your slick bot! 😎\n"
            "Tap a button to see what I can do!\n\n"
            "Commands: /help, /info, /photo, /stat, /members, /top, /mute, /unmute, /active, /rank, /warn, /kick, /afk, /waifus..."
        )
        if query:
            await query.edit_message_text(text=help_text, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat.id, text=help_text, reply_markup=reply_markup)
    else:
        data = query.data
        summaries = {
            "help_info": "ℹ️ /info - Shows user PFP + dope details!",
            "help_photo": "📸 /photo - Grabs recent PFPs!",
            "help_stat": "📊 /stat - Leaderboard with top chatters!",
            "help_members": "👥 /members - Tags all members (admin only)!",
            "help_top": "🏆 /top - Top 3 chatterboxes!",
            "help_mute": "🔇 /mute - Mutes a user (admin only)!",
            "help_unmute": "🔊 /unmute - Unmutes a user (admin only)!",
            "help_active": "🌟 /active - Counts active users!",
            "help_rank": "🥇 /rank - Top 5 message senders!",
            "help_warn": "⚠️ /warn - Warns a user (admin only)!",
            "help_kick": "👢 /kick - Kicks a user (admin only)!",
            "help_afk": "😴 /afk - Mark yourself AFK with a custom message!"
        }
        fun_summaries = {
            "fun_waifu": "🎀 /waifu - Summon a waifu pic!",
            "fun_neko": "🐾 /neko - Catgirl vibes incoming!",
            "fun_shinobu": "🍬 /shinobu - Shinobu-chan says hi!",
            "fun_megumin": "💥 /megumin - Explosive cuteness!",
            "fun_bully": "😈 /bully - Bully someone (playfully)!",
            "fun_cuddle": "🤗 /cuddle - Snuggle up with a reply!",
            "fun_cry": "😢 /cry - Tears everywhere!",
            "fun_hug": "🫂 /hug - Hug it out!",
            "fun_awoo": "🐺 /awoo - Howl like a wolf!",
            "fun_kiss": "💋 /kiss - Smooch someone!",
            "fun_lick": "👅 /lick - Lick attack!",
            "fun_pat": "✋ /pat - Pat-pat!",
            "fun_smug": "😏 /smug - Smug face on!",
            "fun_bonk": "🔨 /bonk - Bonk ‘em!",
            "fun_yeet": "🚀 /yeet - Yeet someone outta here!",
            "fun_blush": "😳 /blush - Get shy!",
            "fun_smile": "😊 /smile - Spread some smiles!",
            "fun_wave": "👋 /wave - Wave hello!",
            "fun_highfive": "✋ /highfive - High-five time!",
            "fun_handhold": "🤝 /handhold - Hold hands, aww!",
            "fun_nom": "🍽️ /nom - Nom nom nom!",
            "fun_bite": "🦷 /bite - Chomp chomp!",
            "fun_glomp": "🏃‍♂️ /glomp - Tackle hug!",
            "fun_slap": "👊 /slap - Slap someone silly!",
            "fun_kill": "💀 /kill - Dramatic kill!",
            "fun_kick": "👟 /kick - Fun kick (not real)!",
            "fun_happy": "🎉 /happy - Happy vibes!",
            "fun_wink": "😉 /wink - Wink wink!",
            "fun_poke": "👉 /poke - Poke poke!",
            "fun_dance": "💃 /dance - Bust a move!",
            "fun_cringe": "😬 /cringe - Cringe moment!"
        }
        
        if data in summaries:
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_back")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(summaries[data], reply_markup=reply_markup)
        elif data == "help_fun":
            fun_keyboard = [
                [InlineKeyboardButton("🎀 Waifu", callback_data="fun_waifu"),
                 InlineKeyboardButton("🐾 Neko", callback_data="fun_neko")],
                [InlineKeyboardButton("🍬 Shinobu", callback_data="fun_shinobu"),
                 InlineKeyboardButton("💥 Megumin", callback_data="fun_megumin")],
                [InlineKeyboardButton("😈 Bully", callback_data="fun_bully"),
                 InlineKeyboardButton("🤗 Cuddle", callback_data="fun_cuddle")],
                [InlineKeyboardButton("😢 Cry", callback_data="fun_cry"),
                 InlineKeyboardButton("🫂 Hug", callback_data="fun_hug")],
                [InlineKeyboardButton("🐺 Awoo", callback_data="fun_awoo"),
                 InlineKeyboardButton("💋 Kiss", callback_data="fun_kiss")],
                [InlineKeyboardButton("👅 Lick", callback_data="fun_lick"),
                 InlineKeyboardButton("✋ Pat", callback_data="fun_pat")],
                [InlineKeyboardButton("😏 Smug", callback_data="fun_smug"),
                 InlineKeyboardButton("🔨 Bonk", callback_data="fun_bonk")],
                [InlineKeyboardButton("🚀 Yeet", callback_data="fun_yeet"),
                 InlineKeyboardButton("😳 Blush", callback_data="fun_blush")],
                [InlineKeyboardButton("😊 Smile", callback_data="fun_smile"),
                 InlineKeyboardButton("👋 Wave", callback_data="fun_wave")],
                [InlineKeyboardButton("✋ Highfive", callback_data="fun_highfive"),
                 InlineKeyboardButton("🤝 Handhold", callback_data="fun_handhold")],
                [InlineKeyboardButton("🍽️ Nom", callback_data="fun_nom"),
                 InlineKeyboardButton("🦷 Bite", callback_data="fun_bite")],
                [InlineKeyboardButton("🏃‍♂️ Glomp", callback_data="fun_glomp"),
                 InlineKeyboardButton("👊 Slap", callback_data="fun_slap")],
                [InlineKeyboardButton("💀 Kill", callback_data="fun_kill"),
                 InlineKeyboardButton("👟 Kick", callback_data="fun_kick")],
                [InlineKeyboardButton("🎉 Happy", callback_data="fun_happy"),
                 InlineKeyboardButton("😉 Wink", callback_data="fun_wink")],
                [InlineKeyboardButton("👉 Poke", callback_data="fun_poke"),
                 InlineKeyboardButton("💃 Dance", callback_data="fun_dance")],
                [InlineKeyboardButton("😬 Cringe", callback_data="fun_cringe")]
            ]
            fun_keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="help_back")])
            reply_markup = InlineKeyboardMarkup(fun_keyboard)
            await query.edit_message_text("🎉 Yo, pick a fun vibe! 🎉", reply_markup=reply_markup)
        elif data.startswith("fun_"):
            cmd = data.split("_")[1]
            back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="help_fun")]]
            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(fun_summaries[f"fun_{cmd}"], reply_markup=reply_markup)