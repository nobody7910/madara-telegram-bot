# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or '7702619386:AAEXCt9dt3SfcW5xZN4FKN77jr0HURovZS0'
API_ID = os.getenv('23882380')
API_HASH = os.getenv('717f0a9521573f91562c2b3bd38f0b3c')