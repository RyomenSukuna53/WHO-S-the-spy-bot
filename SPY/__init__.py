import os
from pyrogram import Client


API_ID = int(os.getenv("API_ID")) 
API_HASH = os.getenv("API_HASH") 
TOKEN = os.getenv("TOKEN") 
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID")) 

bot = Client(api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN) 

