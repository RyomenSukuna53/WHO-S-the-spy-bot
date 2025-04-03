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

# Command: Add Sudo
@bot.on_message(filters.command("addsudo") & filters.user(BOT_OWNER_ID))
async def add_sudo(_, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "Usage: `/addsudo <user_id>`",
            parse_mode=ParseMode.MARKDOWN)
        return

    try:
        user_id = int(message.command[1])
        if users_col.find_one({"user_id": user_id}):
            users_col.update_one({"user_id": user_id}, {"$set": {"is_sudo": True}})
            await message.reply(f"✅ User `{user_id}` added to sudo list.", parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply(f"⚠️ User `{user_id}` not found in the database.", parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await message.reply("❌ Invalid user ID.")

# Command: Remove Sudo
@bot.on_message(filters.command("rsudo") & filters.user(BOT_OWNER_ID))
async def remove_sudo(_, message: Message):
    if len(message.command) != 2:
        await message.reply(
            "Usage: `/rsudo <user_id>`",
            parse_mode=ParseMode.MARKDOWN)
        return

    try:
        user_id = int(message.command[1])
        if users_col.find_one({"user_id": user_id, "is_sudo": True}):
            users_col.update_one({"user_id": user_id}, {"$set": {"is_sudo": False}})
            await message.reply(f"✅ User `{user_id}` removed from sudo list.", parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply(f"⚠️ User `{user_id}` is not in the sudo list.", parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await message.reply("❌ Invalid user ID.")

# Command: Sudo List
@bot.on_message(filters.command("sudolist") & (filters.user(BOT_OWNER_ID) | filters.user(get_sudo_users())))
async def sudolist(_, message: Message):
    sudo_users = await get_sudo_users()  # Await the async function
    if not sudo_users:
        await message.reply("⚠️ No sudo users added yet.")
        return

    sudo_users_list = "\n".join([f"• {user_id}" for user_id in sudo_users])
    await message.reply(f"👥 **Sudo Users List**:\n\n{sudo_users_list}")

# Command: Bot Statistics
# Command: Bot Statistics
@bot.on_message(filters.command("stats") & (filters.user(BOT_OWNER_ID) | filters.user(get_sudo_users())))
async def stats(_, message: Message):
    user_count = await users_col.count_documents({})  # Await async MongoDB operation
    group_count = await group_col.count_documents({})  # Await async MongoDB operation
    banned_count = await users_col.count_documents({"banned": True})  # Await async MongoDB operation

    await message.reply(
        f" **Total Stats**\n\n"
        f"``✨ **Total Users**: {user_count}``\n"
        f"``🔥 **Total Groups**: {group_count}``\n"
        f"``☠️ **Banned Users**: {banned_count}``"
    )
