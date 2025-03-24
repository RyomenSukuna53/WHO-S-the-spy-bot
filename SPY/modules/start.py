from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from SPY import bot
from datetime import datetime
from SPY.db import users_col, active_games_col # Ensure this is connected to your MongoDB
from pyrogram.enums import ChatType
import asyncio
from datetime import datetime, timedelta


@bot.on_message(filters.command("start"))
async def start_command(_, message: Message):
    """
    Handles the /start command to onboard users into the bot.
    If in group chats, it prompts users to start in private.
    """
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    first_name = message.from_user.first_name or "there"

    chat_type = message.chat.type
    print("Chat Type:", chat_type)  # Debug the chat type value

    user = users_col.find_one({"user_id": user_id})
    active_game = active_games_col.find_one(
        {"status": "waiting", "end_time": {"$gte": datetime.utcnow()}}
    )


    # Handle group and supergroup chats
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:  # Direct string comparison
        await message.reply_photo( 
            photo="https://files.catbox.moe/netqsi.jpg",
            caption="**Select the game mode:**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("FRUITS 🍍🍎🍓🍇", callback_data="fruits"),
                        InlineKeyboardButton("CRICKETER 🏏", callback_data="cricket"),
                    ],
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
                ]
            ),
        )
    else:  # Private chat logic
        users_col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "firstname": first_name,
                    "username": username,
                    "start_date": datetime.utcnow(),
                    "goals": 0,
                    "turns": 0,
                }
            },
            upsert=True
        )
        await message.reply(
            f""" 
[{first_name}](tg://user?id={user_id})🚀🚀🚀 Welcome to Ultimate [𝗪𝗛𝗢 𝗜𝗦 𝗧𝗛𝗘 𝗦𝗣𝗬] Bot!
GET READY TO PLAY!. 
<blockquote><b>RULES:
★GAME START AND PLAYERS HAVE TO JOIN THE GAME. 
★MINIMUM 4 PLAYERS NEEDED TO START THE GAME. 
★ALL PLAYERS HAVE SAME WORD EXCEPT ONE(WHO IS THE SPY). 
★ALL PLAYERS HAVE TO DESCRIBE THEIR WORD. 
★YOU HAVE TO VOTE AND GET THE SPY YOU CAN'T GUESS YOU LOSS.</b></blockquote>

Play and enjoy and get relax by playing this. 💥💥💥
""")
        return
        
    if active_game:
        await message.reply("⚠️There is already active game in this group wait for it end.")

  
