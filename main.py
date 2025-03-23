import random
import asyncio
from pyrogram import Client, filters

# Bot Credentials
API_ID = "apni api id daalo"
API_HASH = "apni api hash daalo"
BOT_TOKEN = "apna bot token daalo"
ADMIN_ID = telegram id # Replace with your Telegram ID

bot = Client("whos_the_spy_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
games = {}

# ✅ /start command (Welcome Message)
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("👋 Welcome to **'Who's the Spy'** game! 🕵️\n\nUse:\n- `/startgame@the0_spybot` to start a game\n- `/join` to join an ongoing game\n- `/vote` (reply to a player) to vote out the spy!\n\nAdmin Commands:\n- `/broadcast <msg>` to send a message to all users.")

# ✅ /startgame@the0_spybot command (Game Start)
@bot.on_message(filters.command("startgame@the0_spybot"))
async def new_game(client, message):
    chat_id = message.chat.id
    if chat_id in games:
        await message.reply("⚠️ A game is already in progress! Type `/join` to participate.")
        return

    games[chat_id] = {"players": [], "started": False, "spy": None, "word": None}
    await message.reply("🕵️ A new game has started! Type `/join` to participate.")

# ✅ /join command (Joining Game)
@bot.on_message(filters.command("join"))
async def join_game(client, message):
    chat_id = message.chat.id
    if chat_id not in games:
        await message.reply("⚠️ No active game! Start one with `/startgame@the0_spybot`.")
        return

    if message.from_user.id in games[chat_id]["players"]:
        await message.reply("✅ You have already joined!")
        return

    games[chat_id]["players"].append(message.from_user.id)
    await message.reply(f"👤 {message.from_user.first_name} joined the game!")

# ✅ Assigning Roles and Starting the Game
@bot.on_message(filters.command("begin"))
async def start_game(client, message):
    chat_id = message.chat.id
    if chat_id not in games or len(games[chat_id]["players"]) < 3:
        await message.reply("⚠️ At least 3 players are needed to start the game.")
        return

    words = ["Apple", "Banana", "Car", "Tiger", "Mountain"]
    word = random.choice(words)
    spy = random.choice(games[chat_id]["players"])

    games[chat_id]["word"] = word
    games[chat_id]["spy"] = spy
    games[chat_id]["started"] = True

    for player in games[chat_id]["players"]:
        if player == spy:
            await bot.send_message(player, "🤫 You are the **SPY**! Try to blend in.")
        else:
            await bot.send_message(player, f"🔍 Your secret word is: **{word}**")

    await message.reply("🎮 Game started! Discuss and find the spy. Use `/vote` (reply to a user) to vote!")

# ✅ Voting System
@bot.on_message(filters.command("vote"))
async def vote(client, message):
    chat_id = message.chat.id
    if chat_id not in games or not games[chat_id]["started"]:
        await message.reply("⚠️ No active game! Start one with `/startgame@the0_spybot`.")
        return

    if not message.reply_to_message:
        await message.reply("⚠️ Reply to a player's message to vote them out.")
        return

    voted_out = message.reply_to_message.from_user.id
    spy = games[chat_id]["spy"]

    if voted_out == spy:
        await message.reply(f"🎉 Congratulations! {message.reply_to_message.from_user.first_name} was the **SPY**!")
    else:
        await message.reply(f"❌ Wrong guess! The real SPY was **{spy}**.")

    del games[chat_id]  # End the game

# ✅ Admin Broadcast Message
@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(client, message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("⚠️ Usage: `/broadcast <message>`")
        return

    broadcast_message = text[1]
    users = [user for game in games.values() for user in game["players"]]

    for user in set(users):
        try:
            await bot.send_message(user, f"📢 **Broadcast Message:**\n\n{broadcast_message}")
        except Exception:
            continue

    await message.reply("✅ Broadcast sent successfully!")

bot.run()
