from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
import logging
from SPY.db import group_col  # Assuming you have a collection for groups in your database
from SPY import bot 


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Middleware: Track Group Activity
@bot.on_message(filters.group)
async def track_group_activity(_, message: Message):
    """
    Middleware to track group activity by updating the message count and last active time.
    """
    try:
        group_col.update_one(
            {"chat_id": message.chat.id},
            {
                "$inc": {"messages_count": 1},
                "$set": {"last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            },
            upsert=True
        )
        logger.info(f"grp added to db: {message.chat.title} (ID: {message.chat.id})")
    except Exception as e:
        logger.error(f"Error tracking activity for group {message.chat.title} (ID: {message.chat.id}): {e}")
