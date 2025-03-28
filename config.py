import os
from os import getenv

API_ID = int(getenv("API_ID", "18990697"))
API_HASH = getenv("API_HASH", "f4815b9a16cb03c2f5eabe8db1cb0903")
TOKEN = getenv("TOKEN", "7506827691:AAGRtD6TrW3vDopi_-UnVETI9J5DcoS7nTU")
BOT_OWNER_ID = list(map(int, getenv("OWNER", "6239769036").split(',')))
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/Dragon_ballsopport_Xprobot") 
