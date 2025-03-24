import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
for pyrogram import client, filters

MONGO_URI = "mongodb+srv://shekhikrar026:vmDYM8pQDo07OJk9@cluster0.f9x5k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGO_URI) 

# Collections
users_col = fb["users"]
group_col = fb["groups"]
ban_col = fb["banned_users"]
active_games_col = fb["games"]

async def test_mongo_connection():
    """Tests MongoDB connection."""
    try:
        await mongo_client.server_info()  # This will raise an error if the connection fails
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

async def create_game(group_id, creator_id, creator_name, mode):
    """Creates a new game entry in the database."""
    game_data = {
        "group_id": group_id,
        "mode": mode,
        "players": [creator_id],
        "defenders": [],
        "attackers": [],
        "warnings": {},
        "current_turn": creator_id,
        "start_time": None,
        "status": "waiting"
    }
    result = await active_games_col.insert_one(game_data)
    return result.inserted_id

async def update_game(game_id, update_data):
    """Updates an existing game with new data."""
    await active_games_col.update_one({"_id": game_id}, {"$set": update_data})

async def get_game_by_group(group_id):
    """Fetches an active game for a specific group."""
    return await active_games_col.find_one({"group_id": group_id, "status": {"$in": ["waiting", "active"]}})

async def add_player_to_game(game_id, player_id):
    """Adds a player to an existing game."""
    await active_games_col.update_one({"_id": game_id}, {"$addToSet": {"players": player_id}})


async def remove_game(game_id):
    """Removes a game from the database."""
    if not isinstance(game_id, ObjectId):
        try:
            game_id = ObjectId(game_id)  # Convert to ObjectId
        except Exception as e:
            print(f"❌ Invalid game_id: {e}")
            return

    result = await active_games_col.delete_one({"_id": game_id})
    if result.deleted_count > 0:
        print(f"✅ Game {game_id} deleted successfully.")
    else:
        print(f"⚠️ No game found with ID {game_id}.")
# Run connection test
