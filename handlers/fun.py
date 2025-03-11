# handlers/fun.py
import logging
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

logger = logging.getLogger(__name__)

async def fetch_waifu_image(category: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.waifu.pics/sfw/{category}") as resp:
            data = await resp.json()
            return data["url"]

async def generic_fun_command(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Yo, this only works in groups!")
        return
    
    target = user
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    
    image_url = await fetch_waifu_image(category)
    caption = f"{user.first_name} {category}s {target.first_name}!"
    await context.bot.send_photo(chat_id=chat.id, photo=image_url, caption=caption)

# Define commands
FUN_COMMANDS = {
    "waifus": "waifu", "neko": "neko", "shinobu": "shinobu", "megumin": "megumin",
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