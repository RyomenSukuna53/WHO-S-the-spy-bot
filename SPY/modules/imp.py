import asyncio
from SPY import bot
from pyrogram import filters
from pyrogram.types import Message, ChatMember
from datetime import datetime
from SPY.db import users_col, active_games_col
from pyrogram.enums import ChatType, ChatMemberStatus, ParseMode


# For end_command
@bot.on_message(filters.command("end") & filters.group)
async def end_command(_, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Ensure the command is being used in a group or supergroup
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("❌ This command can only be used in group chats.")
        return

    # Get the chat member object to check the user's status
    chat_member = await bot.get_chat_member(chat_id, user_id)

    # Fetch active game asynchronously
    active_game = await active_games_col.find_one({"status": {"$in": ["active", "waiting"]}})

    if not active_game:
        await message.reply("❌ No active game to end.")
        return

    # Check if the user is the game creator or a group admin
    creator_id = active_game.get("creator_id")
    creator_name = active_game.get("creator_name", "Unknown")

    if user_id != creator_id and chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("⚠️ Only the game creator or a group admin can end the game.")
        return

    # End the game
    await active_games_col.update_one(
        {"_id": active_game["_id"]},
        {"$set": {"status": "ended"}}
    )

    # Notify players
    players = active_game["players"]
    mentions = []

    for player in players:
        user = await users_col.find_one({"user_id": player})  # Awaiting the user fetch
        if user:
            first_name = user.get('firstname', 'Player')
            mentions.append(f"[{first_name}](tg://user?id={player})")
        else:
            mentions.append(f"Player {player}")

    mentions_list = ", ".join(mentions) if mentions else "No players found in the database."

    await bot.send_message(
        chat_id=chat_id,
        text=(
            f"❌ The game created by [{creator_name}](tg://user?id={creator_id}) "
            f"has been ended.\n👥 Players: {mentions_list}"
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    
# For join_command
@bot.on_message(filters.command("join") & filters.group)
async def join_command(_, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name or "there"
    chat_id = message.chat.id

    # Fetch active game asynchronously
    active_game = await active_games_col.find_one(
        {"group_id": chat_id, "status": "waiting"}
    )

    if not active_game:
        await message.reply("❌ No active game to join right now.")
        return

    # Check if the user is already in the game
    if user_id in active_game["players"]:
        await message.reply(f"⚠️ {first_name}, you are already in the game.")
        return

    # Add the user to the game asynchronously
    await active_games_col.update_one(
        {"_id": active_game["_id"]},
        {"$push": {
            "players": user_id,
            "players_name": first_name,
            "players_username": username,
        }}
    )

    await message.reply(f"🎉 {first_name}, you have successfully joined the game!")
    

@bot.on_message(filters.command("members_list") & filters.group)
async def members_list_command(_, message: Message):
    """
    Displays the list of joined members in the active game and mentions their usernames or first names.
    """
    group_id = message.chat.id
    
    # Fetch active game data
    active_game = await active_games_col.find_one({"group_id": group_id, "status": {"$in": ["active", "waiting"]}})
    
    if not active_game:
        return await message.reply("❌ No active game right now.")

    players = active_game.get("players", [])
    
    if not players:
        return await message.reply("🚫 No players have joined yet.")

    # Fetch usernames/names from Telegram API
    player_mentions = await asyncio.gather(
        *[get_player_mention(bot, player_id) for player_id in players]
    )

    # Format the player list
    mentions = [f"{i+1}. {mention}" for i, mention in enumerate(player_mentions)]
    members_list = "\n".join(mentions)

    await message.reply(
        f"👥 **Solo Players:**\n\n{members_list}",
        parse_mode=ParseMode.MARKDOWN
    )


async def get_player_mention(bot, player_id):
    """
    Fetches the player's username or first name directly from Telegram.
    """
    try:
        user = await bot.get_users(player_id)
        if user.username:
            return f"@{user.username}"
        return f"[{user.first_name}](tg://user?id={player_id})"
    except Exception:
        return f"User {player_id}"
        
@bot.on_message(filters.command("leave") & filters.group)
async def leave_command(_, message: Message):
    """
    Allows a user to leave the active game.
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "there"
    username = message.from_user.username or "Unknown"  # Fetch username

    # Await the active game fetch to get the actual result
    active_game = await active_games_col.find_one(
        {"status": "waiting", "end_time": {"$gte": datetime.utcnow()}}
    )

    if not active_game:
        await message.reply("❌ No active game to leave.")
        return

    # Check if the user is in the game
    if user_id not in active_game["players"]:
        await message.reply(f"⚠️ {first_name}, you are not part of the game.")
        return

    # Remove the user from the game
    await active_games_col.update_one(
        {"_id": active_game["_id"]},
        {"$pull": {
            "players": user_id,
            "players_name": first_name,
            "players_username": username,  # Fix: Use the username fetched from the message
        }}
    )

    await message.reply(f"👋 {first_name}, you have left the game.")
