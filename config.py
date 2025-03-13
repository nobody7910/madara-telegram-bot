# config.py
import os
from dotenv import load_dotenv

load_dotenv('/workspaces/madara-telegram-bot/.env')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
MONGO_URI = os.getenv('MONGO_URI')

print(f"Loaded BOT_TOKEN: {BOT_TOKEN}")
print(f"Loaded MONGO_URI: {MONGO_URI}")