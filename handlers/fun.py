# handlers/fun.py
import logging
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

logger = logging.getLogger(__name__)

async def fetch_waifu_image(category: str) -> str:
    """Fetch an image URL from the Waifu.pics API for a given category."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.waifu.pics/sfw/{category}") as resp:
            data = await resp.json()
            if "url" not in data:
                logger.error(f"Invalid category or API response for {category}: {data}")
                return "https://via.placeholder.com/300"  # Fallback image if API fails
            return data["url"]

def get_user_tag(user) -> str:
    """Generate a Telegram user link with username or first name in Markdown format."""
    if user.username:
        return f"[@{user.username}](tg://user?id={user.id})"
    return f"[{user.first_name}](tg://user?id={user.id})"

# Custom captions for each command
FUN_CAPTIONS = {
    "waifu": "{user} summons a dazzling waifu for {target}! 🌸✨",
    "neko": "{user} unleashes a neko cuddle on {target}! 😺💖",
    "shinobu": "{user} channels Shinobu’s grace for {target}! ⚔️🌟",
    "megumin": "{user} explodes {target} with Megumin magic! 💥🔥",
    "bully": "{user} teases {target} with a sly bully move! 😈👊",
    "cuddle": "{user} snuggles {target} in a warm cuddle! 🥰🤗",
    "cry": "{user} floods {target} with dramatic tears! 😢💦",
    "hug": "{user} wraps {target} in a mega hug! 🤗💞",
    "awoo": "{user} howls an epic awoo at {target}! 🐺🌙",
    "kiss": "{user} smacks a sweet kiss on {target}! 💋😘",
    "lick": "{user} sneaks a cheeky lick on {target}! 👅😏",
    "pat": "{user} gives {target} a gentle pat-pat! ✋🥳",
    "smug": "{user} flashes a smug grin at {target}! 😏✨",
    "bonk": "{user} bonks {target} with a mighty whack! 🔨💥",
    "yeet": "{user} yeets {target} into the stratosphere! 🚀🌌",
    "blush": "{user} turns {target} red with a blush! 😳💖",
    "smile": "{user} lights up {target} with a bright smile! 😊🌞",
    "wave": "{user} sends {target} a cheerful wave! 👋🎉",
    "highfive": "{user} slams a high-five on {target}! 🖐️🔥",
    "handhold": "{user} grabs {target} for a sweet handhold! 🤝💕",
    "nom": "{user} noms {target} like a tasty snack! 🍽️😋",
    "bite": "{user} chomps {target} with a playful bite! 🦷😈",
    "glomp": "{user} tackles {target} in a wild glomp! 💖🏃",
    "slap": "{user} lands a legendary slap on {target}! ✋💥",
    "kill": "{user} obliterates {target} in dramatic fashion! ⚰️💀",
    "kickk": "{user} boots {target} with a stylish kick! 👢💨",  # Maps to "slap" image
    "happy": "{user} showers {target} with pure happiness! 🎉😄",
    "wink": "{user} winks at {target} with a sly charm! 😉✨",
    "poke": "{user} pokes {target} for some fun! 👈😆",
    "dance": "{user} grooves with {target} in a wild dance! 💃🕺",
    "cringe": "{user} cringes hard at {target}! 😬😂"
}

async def generic_fun_command(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str) -> None:
    """Handle generic fun commands with Waifu.pics images and custom tagged captions."""
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Yo, this only works in groups!")
        return
    
    target = user  # Default to self if no reply
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    
    # Fetch image from Waifu.pics API
    image_url = await fetch_waifu_image(category)
    
    # Get user tags
    user_tag = get_user_tag(user)
    target_tag = get_user_tag(target)
    
    # Get custom caption and format it
    caption_template = FUN_CAPTIONS.get(category, "{user} {category}s {target}!")  # Fallback
    caption = caption_template.format(user=user_tag, target=target_tag)
    
    # Send photo with custom caption
    await context.bot.send_photo(
        chat_id=chat.id,
        photo=image_url,
        caption=caption,
        parse_mode="Markdown"
    )

# Define commands with their corresponding Waifu.pics categories
FUN_COMMANDS = {
    "waifus": "waifu", "neko": "neko", "shinobu": "shinobu", "megumin": "megumin",
    "bully": "bully", "cuddle": "cuddle", "cry": "cry", "hug": "hug", "awoo": "awoo",
    "kiss": "kiss", "lick": "lick", "pat": "pat", "smug": "smug", "bonk": "bonk",
    "yeet": "yeet", "blush": "blush", "smile": "smile", "wave": "wave",
    "highfive": "highfive", "handhold": "handhold", "nom": "nom", "bite": "bite",
    "glomp": "glomp", "slap": "slap", "kill": "kill", "kickk": "slap",  # Maps to "slap" category
    "happy": "happy", "wink": "wink", "poke": "poke", "dance": "dance", "cringe": "cringe"
}

def register_fun_handlers(application):
    """Register all fun command handlers with the application."""
    for cmd, category in FUN_COMMANDS.items():
        application.add_handler(CommandHandler(cmd, lambda u, c, cat=category: generic_fun_command(u, c, cat)))