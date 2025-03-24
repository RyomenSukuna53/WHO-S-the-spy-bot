import asyncio
from SPY import bot
from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime
from SPY.db import users_col, active_games_col
from pyrogram.enums import ChatType, ChatMemberStatus, ParseMode


# 🌟 /join command - Players game join kar sakte hain
@bot.on_message(filters.command("join") & filters.group)
async def join_command(_, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name or "Player"
    chat_id = message.chat.id

    # Active game check karo
    active_game = active_games_col.find_one({"chat_id": chat_id, "status": "waiting"})
    
    if not active_game:
        await message.reply("❌ THERE IS NO ACTIVE GAME IN THIS CHAT")
        return

    # Agar user already game mein hai toh
    if any(player["user_id"] == user_id for player in active_game["players"]):
        await message.reply(f"⚠️ {first_name}, You Are Already In The Game!")
        return

    # User ko game mein add karo
    player_data = {"user_id": user_id, "name": first_name, "role": "unknown"}
    active_games_col.update_one(
        {"_id": active_game["_id"]},
        {"$push": {"players": player_data}}
    )

    await message.reply(f">🎉 [{first_name}](tg://user?id={user_id}), Has been joined the game!", parse_mode=enums.ParseMode.MARKDOWN)


# 🌟 /leave command - Players game leave kar sakte hain
@bot.on_message(filters.command("leave") & filters.group)
async def leave_command(_, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Player"
    chat_id = message.chat.id

    # Active game check karo
    active_game = active_games_col.find_one({"chat_id": chat_id, "status": "waiting"})

    if not active_game:
        await message.reply("❌ Koi active game abhi nahi chal raha.")
        return

    # Check karo agar player game mein hai
    if not any(player["user_id"] == user_id for player in active_game["players"]):
        await message.reply(f"⚠️ {first_name}, tum game mein nahi ho.")
        return

    # Player ko game se hatao
    active_games_col.update_one(
        {"_id": active_game["_id"]},
        {"$pull": {"players": {"user_id": user_id}}}
    )

    await message.reply(f"👋 {first_name}, tumne game leave kar diya.")


# 🌟 /members_list command - Jo log game mein hai unki list
@bot.on_message(filters.command("members_list") & filters.group)
async def members_list_command(_, message: Message):
    chat_id = message.chat.id

    # Active game check karo
    active_game = active_games_col.find_one({"chat_id": chat_id, "status": {"$in": ["waiting", "ongoing"]}})

    if not active_game:
        return await message.reply("❌ Koi active game nahi hai.")

    players = active_game.get("players", [])

    if not players:
        return await message.reply("🚫 Koi player abhi tak join nahi hua.")

    # Players list format karo
    mentions = [f"{i+1}. [{p['name']}](tg://user?id={p['user_id']})" for i, p in enumerate(players)]
    members_list = "\n".join(mentions)

    await message.reply(
        f"👥 **Players in Game:**\n\n{members_list}",
        parse_mode=ParseMode.MARKDOWN
    )


# 🌟 /end command - Game creator ya admin game end kar sakta hai
@bot.on_message(filters.command("end") & filters.group)
async def end_command(_, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Group ya supergroup check karo
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("❌ Ye command sirf group mein use kiya ja sakta hai.")
        return

    # Group admin check karo
    chat_member = await bot.get_chat_member(chat_id, user_id)

    # Active game fetch karo
    active_game = active_games_col.find_one({"chat_id": chat_id, "status": "ongoing"})

    if not active_game:
        await message.reply("❌ Koi active game nahi hai jo end kiya ja sake.")
        return

    creator_id = active_game.get("creator_id")

    if user_id != creator_id and chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("⚠️ Sirf game creator ya admin hi game end kar sakta hai.")
        return

    # Game ko "ended" status do
    active_games_col.update_one(
        {"_id": active_game["_id"]},
        {"$set": {"status": "ended"}}
    )

    # Players ko notify karo
    players = active_game["players"]
    mentions = [f"[{p['name']}](tg://user?id={p['user_id']})" for p in players]

    await bot.send_message(
        chat_id=chat_id,
        text=f"❌ Game end ho gaya!\n👥 Players: {', '.join(mentions)}",
        parse_mode=ParseMode.MARKDOWN
    )
