# handlers/fun.py
import logging
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

logger = logging.getLogger(__name__)

# Custom fallback images (replace these with your own hosted URLs)
FALLBACK_IMAGES = {
    "api_down": "https://yourcdn.com/fallback/api_down.jpg",
    "no_image": "https://yourcdn.com/fallback/no_image.jpg",
    "connection": "https://yourcdn.com/fallback/connection.jpg",
    "oops": "https://yourcdn.com/fallback/oops.jpg"
}

async def fetch_waifu_image(category: str) -> str:
    try:
        # More aggressive timeout and SSL tweak
        async with aiohttp.ClientSession() as session:
            logger.info(f"Fetching waifu image for category: {category}")
            async with session.get(
                f"https://api.waifu.pics/sfw/{category}",
                timeout=aiohttp.ClientTimeout(total=5),  # Shorter timeout to fail fast
                ssl=True  # Explicit SSL to avoid default issues
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Waifu API returned {resp.status} for {category}")
                    return FALLBACK_IMAGES["api_down"]
                data = await resp.json()
                url = data.get("url")
                if not url:
                    logger.warning(f"No URL in response for {category}")
                    return FALLBACK_IMAGES["no_image"]
                logger.info(f"Got image URL: {url}")
                return url
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Connection error fetching {category}: {str(e)}")
        return FALLBACK_IMAGES["connection"]
    except aiohttp.ClientError as e:
        logger.error(f"Client error fetching {category}: {str(e)}")
        return FALLBACK_IMAGES["connection"]
    except Exception as e:
        logger.error(f"Unexpected error fetching {category}: {str(e)}")
        return FALLBACK_IMAGES["oops"]

async def generic_fun_command(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Yo, this only works in groups!")
        return
    
    logger.info(f"Fun command /{category} by {user.id} in chat {chat.id}")
    target = user
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    
    image_url = await fetch_waifu_image(category)
    caption = f"{user.first_name} {category}s {target.first_name}!"
    await context.bot.send_photo(chat_id=chat.id, photo=image_url, caption=caption)

FUN_COMMANDS = {
    "waifu": "waifu", "neko": "neko", "shinobu": "shinobu", "megumin": "megumin",
    "bully": "bully", "cuddle": "cuddle", "cry": "cry", "hug": "hug", "awoo": "awoo",
    "kiss": "kiss", "lick": "lick", "pat": "pat", "smug": "smug", "bonk": "bonk",
    "yeet": "yeet", "blush": "blush", "smile": "smile", "wave": "wave",
    "highfive": "highfive", "handhold": "handhold", "nom": "nom", "bite": "bite",
    "glomp": "glomp", "slap": "slap", "kill": "kill", "kick": "kick",
    "happy": "happy", "wink": "wink", "poke": "poke", "dance": "dance", "cringe": "cringe"
}

def register_fun_handlers(application):
    for cmd, category in FUN_COMMANDS.items():
        application.add_handler(CommandHandler(cmd, lambda u, c, cat=category: generic_fun_command(u, c, cat)))