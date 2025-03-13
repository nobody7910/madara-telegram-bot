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

async def generic_fun_command(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str) -> None:
    """Handle generic fun commands with Waifu.pics images and tagged captions."""
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
    
    # Create caption with username links
    user_tag = get_user_tag(user)
    target_tag = get_user_tag(target)
    caption = f"{user_tag} {category}s {target_tag}!"
    
    # Send photo with Markdown-parsed caption
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