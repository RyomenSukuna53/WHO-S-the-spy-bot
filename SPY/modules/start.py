from SPY import bot 
from pyrogram import Client, filters
from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from SPY.db import user_col
from pyrogram.enums import ParseMode

@bot.on_message(filters.command("start") 
async def start_command(client, message):
  user = message.from_user
  first_name = user.first_name
  username = user.username
  user_id = user.id
  chat_type = message.chat.type

  if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
    await message.reply_text(f"[{firstname}](tg://user?id={user_id})\nStarted The game\n>||[𝗪𝗛𝗢 𝗜𝗦 𝗧𝗛𝗘 𝗦𝗣𝗬]||\n\nJOIN THE GAME BY CLICKING THE BUTTON", parse_mode=ParseMode.MARKDOWN, reply_markup = InlineKeyboardMakrup([
      [InlineKeyboardButton("👾𝕁𝕆𝕀ℕ👾", callback_data=f"join_{user_id}")

  else:
    await message.reply_text(f"Hey {first_name} use this command in a group to start the game") 
  
