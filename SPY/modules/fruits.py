from SPY.db import users_col, ban_col, active_game_col
from SPY import bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient
import asyncio
import random

# Word list
words = ["Apple", "Banana", "Mango", "Orange", "Watermelon"]

# Cooldown tracker
cooldown_tracker = {}

# Start Game function
@bot.on_callback_query(filters.regex("fruits"))
async def start_game(client, callback_query):
    chat_id = callback_query.message.chat.id
    players = [user async for user in bot.get_chat_members(chat_id) if not user.user.is_bot]

    if len(players) < 3:
        await callback_query.message.reply("Not enough players to start the game.")
        return

    chosen_word = random.choice(words)
    spy_index = random.randint(0, len(players) - 1)

    game_data = {
        "chat_id": chat_id,
        "word": chosen_word,
        "players": [],
        "spy": players[spy_index].user.id,
        "votes": {},
        "status": "ongoing"
    }

    for i, player in enumerate(players):
        role = "spy" if i == spy_index else "player"
        game_data["players"].append({"user_id": player.user.id, "role": role})
        try:
            if role == "spy":
                await bot.send_message(player.user.id, "You are the spy. Try to blend in!")
            else:
                await bot.send_message(player.user.id, f"The word is: {chosen_word}")
        except:
            await callback_query.message.reply(f"Couldn't send message to {player.user.first_name}. They might have blocked the bot.")

    active_game_col.insert_one(game_data)
    cooldown_tracker[chat_id] = asyncio.get_event_loop().time()  # Start cooldown timer
    await callback_query.message.reply("The game has started! Check your private messages for your role.\n\nVoting will begin after **3 minutes**.")

    # Start countdown for voting
    await asyncio.sleep(180)  # 3-minute cooldown
    await start_voting(client, callback_query.message)

# Voting Function
async def start_voting(client, message):
    chat_id = message.chat.id
    game_data = active_game_col.find_one({"chat_id": chat_id, "status": "ongoing"})
    if not game_data:
        return

    players = game_data["players"]
    
    # Create voting buttons
    vote_buttons = []
    for player in players:
        user_id = player["user_id"]
        user = await bot.get_users(user_id)
        vote_buttons.append([InlineKeyboardButton(user.first_name, callback_data=f"vote_{user_id}")])

    # Skip & Force Vote Options
    vote_buttons.append([
        InlineKeyboardButton("🛑 Skip Voting", callback_data="skip_vote"),
        InlineKeyboardButton("⚡ Force Vote", callback_data="force_vote")
    ])

    keyboard = InlineKeyboardMarkup(vote_buttons)
    
    # Send voting message
    msg = await message.reply("🔴 **Voting Started!** 🔴\n\nVote out the suspected spy!\n\n**Voting ends in 1 minute.**", reply_markup=keyboard)
    
    await asyncio.sleep(60)  # 1-minute voting window

    # End Voting & Remove Player
    await end_voting(client, message, msg)

# Vote Callback Handler
@bot.on_callback_query(filters.regex(r"^vote_"))
async def vote_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    voter_id = callback_query.from_user.id
    voted_user_id = int(callback_query.data.split("_")[1])

    game_data = active_game_col.find_one({"chat_id": chat_id, "status": "ongoing"})
    if not game_data:
        return
    
    if "votes" not in game_data:
        game_data["votes"] = {}

    game_data["votes"][voter_id] = voted_user_id  # Store the vote
    active_game_col.update_one({"chat_id": chat_id}, {"$set": {"votes": game_data["votes"]}})
    
    await callback_query.answer("Vote registered!")
    
# End Voting & Remove Player
async def end_voting(client, message, msg):
    chat_id = message.chat.id
    game_data = active_game_col.find_one({"chat_id": chat_id, "status": "ongoing"})
    if not game_data:
        return
    
    votes = game_data.get("votes", {})
    if not votes:
        await msg.edit_text("No votes were cast. Voting skipped!")
        return

    # Count votes
    vote_count = {}
    for vote in votes.values():
        vote_count[vote] = vote_count.get(vote, 0) + 1
    
    # Get player with highest votes
    max_votes = max(vote_count.values(), default=0)
    eliminated = [user_id for user_id, count in vote_count.items() if count == max_votes]

    if len(eliminated) > 1:
        await msg.edit_text("It's a tie! No one is eliminated this round.")
    else:
        eliminated_user_id = eliminated[0]
        eliminated_player = await bot.get_users(eliminated_user_id)
        
        # Remove from players list
        updated_players = [p for p in game_data["players"] if p["user_id"] != eliminated_user_id]
        active_game_col.update_one({"chat_id": chat_id}, {"$set": {"players": updated_players, "votes": {}}})
        
        await msg.edit_text(f"❌ **{eliminated_player.first_name}** was eliminated!\n\nNext round in **3 minutes.**")

        # Start cooldown timer for next round
        cooldown_tracker[chat_id] = asyncio.get_event_loop().time()
        await asyncio.sleep(180)  # 3-minute cooldown
        await start_voting(client, message)

# Force Vote Command
@bot.on_message(filters.command("force_vote"))
async def force_vote(client, message):
    chat_id = message.chat.id
    if chat_id not in cooldown_tracker or asyncio.get_event_loop().time() - cooldown_tracker[chat_id] > 180:
        await message.reply("⚡ Force voting started!")
        await start_voting(client, message)
    else:
        await message.reply("You cannot start force voting yet!")

# Skip Vote Callback
@bot.on_callback_query(filters.regex("skip_vote"))
async def skip_vote(client, callback_query):
    chat_id = callback_query.message.chat.id
    await callback_query.message.edit_text("🛑 Voting skipped!\n\nNext round in **3 minutes.**")
    
    cooldown_tracker[chat_id] = asyncio.get_event_loop().time()
    await asyncio.sleep(180)  # 3-minute cooldown
    await start_voting(client, callback_query.message)
