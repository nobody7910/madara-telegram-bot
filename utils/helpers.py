from telegram import Bot
import time

bot_start_time = time.time()

async def get_user_photo(bot: Bot, user_id: int) -> str | None:
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.photos:
            return photos.photos[0][-1].file_id
    except:
        return None

async def get_chat_photo(bot: Bot, chat_id: int) -> str | None:
    try:
        chat = await bot.get_chat(chat_id)
        if chat.photo:
            return chat.photo.big_file_id
    except:
        return None

def bot_uptime() -> str:
    uptime = time.time() - bot_start_time
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"