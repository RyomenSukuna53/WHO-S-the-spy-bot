import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://shekhikrar026:vmDYM8pQDo07OJk9@cluster0.f9x5k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGO_URI) 
spy = client["spy_database"]
user_col = spy["users"]
ban_col = spy["banned_users"]

try:
    client.server_info()  # This will raise an error if the connection fails
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
