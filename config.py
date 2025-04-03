import os
from os import getenv

API_ID = int(getenv("API_ID", "27548865"))
API_HASH = getenv("API_HASH", "db07e06a5eb288c706d4df697b71ab61")
TOKEN = getenv("TOKEN", "7769196646:AAGeRD7W0q4KM-c5Ud9QVIKhXKeNdu8chxY")
BOT_OWNER_ID = list(map(int, getenv("OWNER", "6239769036").split(',')))
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/Dragon_ballsopport_Xprobot") 
