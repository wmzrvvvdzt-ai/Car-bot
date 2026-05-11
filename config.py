import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))
MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT", 15))
