from pyrogram import client, filters
from SPY import bot
from SPY.db import users_col, ban_col
from config import BOT_OWNER_ID
from pyrogram.types import Message


# Command: Broadcast
@bot.on_message(filters.command("broadcast") & filters.user(BOT_OWNER_ID))
async def broadcast(_, message: Message):
    if not message.reply_to_message:
        await message.reply("Please reply to the message you want to broadcast.")
        return

    broadcast_message = message.reply_to_message
    users = await users_col.find({"user_id": {"$exists": True}}).to_list(None)  # Await and convert cursor to list
    groups = await group_col.find({"chat_id": {"$exists": True}}).to_list(None)  # Await and convert cursor to list
    success_count, failure_count = 0, 0

    await message.reply("📣 **Broadcast started...**")
    logger.info(f"Broadcast to {len(users)} users and {len(groups)} groups.")

    for user in users:
        try:
            await bot.forward_messages(
                chat_id=user["user_id"],
                from_chat_id=broadcast_message.chat.id,
                message_ids=broadcast_message.id,
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Error sending to user {user['user_id']}: {e}")
            failure_count += 1

    for group in groups:
        try:
            await bot.forward_messages(
                chat_id=group["chat_id"],
                from_chat_id=broadcast_message.chat.id,
                message_ids=broadcast_message.id,
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Error sending to group {group['chat_id']}: {e}")
            failure_count += 1

    await message.reply(
        f"📣 **Broadcast completed.**\n\n"
        f"✅ Sent to {success_count} users/groups.\n"
        f"❌ Failed for {failure_count} users/groups."
    )

